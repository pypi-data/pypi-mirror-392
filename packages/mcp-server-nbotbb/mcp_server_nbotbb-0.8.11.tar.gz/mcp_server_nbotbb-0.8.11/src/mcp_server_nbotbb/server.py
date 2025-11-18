import json
import mysql.connector
from mysql.connector import Error
from typing import Any, Dict, List, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.shared.exceptions import McpError
from datetime import datetime
import re
# version = "0.8.10"
# ========== MySQL 配置 ==========
MYSQL_CONFIG = {
    'host': 'rm-uf659xxpoxch0io8avo.mysql.rds.aliyuncs.com',  
    'port': 3306,
    'user': 'nongshang_user',
    'password': 'NongShang@2024!',
    'database': 'products_db',
    'charset': 'utf8mb4',
    'autocommit': True,
    'pool_name': 'mcp_pool',
    'pool_size': 5
}

import decimal

def _convert_decimal(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)  # 或 str(obj) 如果你希望保留精度
    elif isinstance(obj, dict):
        return {k: _convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_decimal(item) for item in obj]
    else:
        return obj


def agro_product_search_recommend(product_list: List[Dict[str, str]], user_preferences: Dict[str, str] = None) -> Dict[str, Any]:
    connection = None
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)

        final_result = {}

        for prod_query in product_list:
            product_name = prod_query.get("product_name", "").strip()
            main_effect = prod_query.get("main_effect", "").strip()
            brand = prod_query.get("brand", "").strip()  # 可能包含品牌或厂家，如 "滨农 金特"

            found_by_name = False
            all_candidates = []  # list of (prod, sku)

            # === Step 1: Try match by product_name ===
            if product_name:
                cursor.execute("""
                    SELECT prod_id, name, shop_id, image_url
                    FROM products 
                    WHERE name LIKE %s
                """, (f"%{product_name}%",))
                prods_by_name = cursor.fetchall()

                for p in prods_by_name:
                    cursor.execute("""
                        SELECT sku_id, price, stocks, package_spec, production_date 
                        FROM product_skus 
                        WHERE prod_id = %s AND stocks > 0
                    """, (p["prod_id"],))
                    skus = cursor.fetchall()
                    for sku in skus:
                        all_candidates.append((p, sku))
                
                if all_candidates:
                    found_by_name = True

            # === Step 2: If no result by name, try main_effect ===
            if not all_candidates and main_effect:
                cursor.execute("""
                    SELECT prod_id, name, shop_id, image_url
                    FROM products 
                    WHERE name LIKE %s
                """, (f"%{main_effect}%",))
                prods_by_effect = cursor.fetchall()

                for p in prods_by_effect:
                    cursor.execute("""
                        SELECT sku_id, price, stocks, package_spec, production_date 
                        FROM product_skus 
                        WHERE prod_id = %s AND stocks > 0
                    """, (p["prod_id"],))
                    skus = cursor.fetchall()
                    for sku in skus:
                        all_candidates.append((p, sku))

            # === Step 3: Filter & Rank candidates ===
            ranked = []

            for prod, sku in all_candidates:
                score = 0

                # Brand/Shop matching: if brand is provided, boost matches
                if brand:
                    # Simple heuristic: check if brand appears in prod name or we have shop info?
                    # Since we don't have a 'brand' column, assume brand may appear in `name`
                    full_text = f"{prod['name']} {prod.get('shop_id', '')}".lower()
                    brand_lower = brand.lower()
                    if brand_lower in full_text:
                        score += 100  # strong boost

                # Price preference
                price = float(sku["price"]) if sku["price"] else float('inf')
                if user_preferences and user_preferences.get("price_preference") == "cheapest":
                    # Lower price = better → use negative price as score component
                    score -= price * 0.1  # scale down to avoid dominating
                elif user_preferences and user_preferences.get("price_preference") == "premium":
                    score += price * 0.1

                # Date preference
                prod_date = sku["production_date"]
                if prod_date and user_preferences and user_preferences.get("date_preference") == "recent":
                    if isinstance(prod_date, str):
                        prod_date = datetime.strptime(prod_date, "%Y-%m-%d").date()
                    days_old = (datetime.today().date() - prod_date).days
                    score -= days_old * 0.01  # newer = higher score

                ranked.append({
                    "product": prod,
                    "sku": sku,
                    "score": score,
                    "match_type": "exact" if found_by_name else "recommend"
                })

            # Sort by score descending
            ranked.sort(key=lambda x: x["score"], reverse=True)

            # Take top 2
            top_results = ranked[:2]

            # Format output
            key = product_name if product_name else main_effect
            final_result[key] = {
                "match_type": "exact" if found_by_name else "recommend",
                "results": [
                    {
                        "product": r["product"],
                        "sku": r["sku"]
                    } for r in top_results
                ]
            }

        results = _convert_decimal(final_result)
        return {"message": "Success", "data": results}

    except Exception as e:
        return {"message": "Error", "error": str(e)}
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def extract_delivery_address(
    name: str = "", phone: str = "", province: str = "",
    city: str = "", district: str = "", detailed_address: str = "", postal_code: str = ""
) -> Dict[str, Any]:
    if province == city:
        city = ""
    cleaned = {
        "name": name.strip(),
        "phone": phone.strip(),
        "province": province.strip(),
        "city": city.strip(),
        "district": district.strip(),
        "detailed_address": detailed_address.strip(),
        "postal_code": postal_code.strip()
    }
    return {"message": "Success", "data": cleaned}

# ========== MCP Server ==========
async def serve(db_path: str) -> None:
    # 注意：现在 db_path 参数不再使用，但保留签名以兼容启动方式
    server = Server("nbotbb-agro-mcp")
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="agro_product_search_recommend",
                description="根据结构化商品列表查询农资库存与价格，根据用户偏好推荐",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "product_list": {
                            "type": "array",
                            "description": "商品查询列表，从用户输入中提取商品信息。",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "product_name": {
                                        "type": "string",
                                        "description": "产品名称和关键成分的合并，如'烯草酮'、'烟嘧磺隆 二甲4氯纳'"
                                    },
                                    "brand": {
                                        "type": "string",
                                        "description": "品牌和生产厂家的合并，如'滨农 金特'、'青岛金尔农化 农母'"
                                    },
                                    "specification": {
                                        "type": "string",
                                        "description": "产品规格，如'200毫升'、'100g'"
                                    },
                                    "main_effect": {
                                        "type": "string",
                                        "description": "主要作用，基于产品名或成分推断，如'玉米田除草'、'增甜改善品质'"
                                    }
                                },
                                "required": ["main_effect"],
                                "additionalProperties": False
                            }
                        },
                        "user_preferences": {
                            "type": "object",
                            "description": "用户偏好设置。只有当用户明确表达偏好时才设置相应字段，否则完全省略此参数。",
                            "properties": {
                                "price_preference": {
                                    "type": "string",
                                    "enum": ["cheapest", "balanced", "premium"],
                                    "description": "价格偏好：只有当用户明确说'最便宜的'、'便宜点'、'价格实惠'时才设置，否则省略"
                                },
                                "date_preference": {
                                    "type": "string",
                                    "enum": ["recent", "any"],
                                    "description": "生产日期偏好：只有当用户明确说'近期生产的'、'要新日期的'时才设置，否则省略"
                                }
                            },
                            "required": [],
                            "additionalProperties": False
                        }
                    },
                    "required": ["product_list"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="extract_delivery_address",
                description="从用户输入中提取完整的快递地址信息，包括收件人姓名、手机号和详细地址信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "收件人姓名，例如：张三、李四"
                        },
                        "phone": {
                            "type": "string",
                            "description": "收件人手机号码，应为11位数字，例如：13812345678"
                        },
                        "province": {
                            "type": "string",
                            "description": "省份/直辖市，例如：广东省、北京市"
                        },
                        "city": {
                            "type": "string",
                            "description": "城市名称，例如：深圳市、广州市"
                        },
                        "district": {
                            "type": "string",
                            "description": "区/县名称，例如：南山区、海淀区"
                        },
                        "detailed_address": {
                            "type": "string",
                            "description": "街道、门牌号、小区、楼栋、房间号等具体地址信息，例如：科技园南区1栋A座1001室"
                        },
                        "postal_code": {
                            "type": "string",
                            "description": "6位数字邮政编码，例如：518000"
                        }
                    },
                    "required": ["name", "phone", "province", "city", "district", "detailed_address"],
                    "additionalProperties": False
                }
            )
        ]
            
            
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
        try:
            if name == "agro_product_search_recommend":
                res = agro_product_search_recommend(
                    product_list=arguments["product_list"],
                    user_preferences=arguments.get("user_preferences")
                )
            elif name == "extract_delivery_address":
                res = extract_delivery_address(**{k: v for k, v in arguments.items() if k in [
                    "name", "phone", "province", "city", "district", "detailed_address", "postal_code"
                ]})
            else:
                raise ValueError(f"Unknown tool: {name}")

            return [TextContent(type="text", text=json.dumps(res, ensure_ascii=False))]

        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"message": "Error", "error": str(e)}, ensure_ascii=False))]
            

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)