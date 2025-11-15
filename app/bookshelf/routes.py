from flask import Blueprint, render_template, request, jsonify
import requests
import json
import os
from urllib.parse import unquote

bookshelf_bp = Blueprint(
    "bookshelf",
    __name__,
    url_prefix="/bookshelf",
    # template_folder は不要。Flask の templates ディレクトリを使う
)

RAKUTEN_APP_ID = "1077795699367532233"
CALIL_APP_KEY = "a4803b22ab1cf9bd6eda17b6518ea542"
DATA_FILE = "data/shelves.json"

SHELVES = [
    "貯蓄優先型",
    "積立安定型",
    "アクティブチャレンジ型",
    "ステーキング運用型",
    "株式アクティブ型",
    "ハイリスクハイリターン型",
    "テクノロジー志向型",
    "積立応用型",
    "私の本棚",
]

# -----------------------------
# JSON読み書き
# -----------------------------
def load_shelves():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        data = {shelf: [] for shelf in SHELVES}
        save_shelves(data)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_shelves(shelves):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(shelves, f, ensure_ascii=False, indent=2)


# -----------------------------
# 書籍検索API (楽天 / OpenLibrary)
# -----------------------------
def search_openlibrary(title):
    url = "https://openlibrary.org/search.json"
    response = requests.get(url, params={"title": title})
    data = response.json()
    books = []
    for doc in data.get("docs", []):
        isbn = doc.get("isbn", [None])[0]
        books.append(
            {
                "title": doc.get("title", ""),
                "author": ", ".join(doc.get("author_name", [])),
                "isbn": isbn,
                "year": doc.get("first_publish_year", ""),
                "cover": f"https://covers.openlibrary.org/b/id/{doc.get('cover_i',0)}-L.jpg"
                if doc.get("cover_i")
                else "",
                "url": f"https://openlibrary.org{doc.get('key')}",
                "tags": " ".join(doc.get("subject", [])) if doc.get("subject") else "",
                "libraries": [],
            }
        )
    return books


def find_nearby_libraries(lat, lon):
    url = "https://api.calil.jp/library"
    params = {
        "appkey": CALIL_APP_KEY,
        "geocode": f"{lon},{lat}",
        "format": "json",
        "callback": "",
    }
    response = requests.get(url, params=params)
    try:
        libraries = response.json()
    except json.JSONDecodeError:
        libraries = []
    return libraries[:5]


# -----------------------------
# 書籍検索 API エンドポイント
# -----------------------------
@bookshelf_bp.route("/search")
def search_books():
    title = request.args.get("title", "")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not title:
        return jsonify([])

    books = []

    # 楽天API
    url = "https://app.rakuten.co.jp/services/api/BooksBook/Search/20170404"
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "title": title,
        "format": "json",
        "hits": 20,
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    for item in data.get("Items", []):
        book_item = item["Item"]
        books.append(
            {
                "title": book_item.get("title", ""),
                "author": book_item.get("author", ""),
                "isbn": book_item.get("isbn", ""),
                "price": book_item.get("itemPrice", 0),
                "image": book_item.get("largeImageUrl", ""),
                "itemUrl": book_item.get("itemUrl", ""),
                "tags": "",
                "libraries": [],
            }
        )

    # OpenLibrary fallback
    if not books:
        books = search_openlibrary(title)

    # 近場図書館情報
    if lat and lon:
        libs = find_nearby_libraries(float(lat), float(lon))
        for book in books:
            book["libraries"] = []
            for lib in libs:
                try:
                    lib_lat, lib_lon = map(
                        float, lib.get("geocode", "0,0").split(",")[::-1]
                    )
                except:
                    lib_lat, lib_lon = None, None
                book["libraries"].append(
                    {
                        "name": lib.get("formal"),
                        "lat": lib_lat,
                        "lon": lib_lon,
                        "url": f"https://calil.jp/library/{lib.get('systemid')}",
                    }
                )

    return jsonify(books)


# -----------------------------
# トップページ
# -----------------------------
@bookshelf_bp.route("/")
def index():
    return render_template("bookshelf/index.html", shelves=SHELVES)


# -----------------------------
# 「私の本棚」操作 API
# -----------------------------
@bookshelf_bp.route("/add_to_my_shelf", methods=["POST"])
def add_to_my_shelf():
    book = request.get_json().get("book")
    if not book:
        return jsonify({"error": "bookが指定されていません"}), 400
    shelves = load_shelves()
    my = shelves.setdefault("私の本棚", [])
    if not any(b["title"] == book["title"] for b in my):
        my.append(book)
        save_shelves(shelves)
    return jsonify({"my_shelf": my})


@bookshelf_bp.route("/remove_from_my_shelf", methods=["POST"])
def remove_from_my_shelf():
    title = request.get_json().get("title")
    if not title:
        return jsonify({"error": "titleが指定されていません"}), 400
    shelves = load_shelves()
    shelves["私の本棚"] = [b for b in shelves.get("私の本棚", []) if b["title"] != title]
    save_shelves(shelves)
    return jsonify({"my_shelf": shelves["私の本棚"]})


@bookshelf_bp.route("/get_my_shelf")
def get_my_shelf():
    shelves = load_shelves()
    return jsonify({"my_shelf": shelves.get("私の本棚", [])})


# -----------------------------
# 各棚ページ
# -----------------------------
@bookshelf_bp.route("/shelf/<path:name>")
def shelf_page(name):
    name = unquote(name)
    shelves = load_shelves()  # JSON から読み込み
    # 手書きで追加
    shelves["貯蓄優先型"] = [
        {
            "author": "ベンジャミン・グレアム",
            "description": "『賢明なる投資家』の理解度が一気に進む解説付き！",
            "image": "https://thumbnail.image.rakuten.co.jp/@0_mall/book/cabinet/3400/9784775973400_1_2.jpg?_ex=200x200",
            "itemUrl": "https://books.rakuten.co.jp/rb/18327208/?rafcid=wsc_b_bs_1077795699367532233",
            "price": 4180,
            "title": "新　賢明なる投資家（下）第3版",
        },
        {
            "author": "両＠リベ大学長",
            "description": "142万部突破の『お金の大学』が超・パワーアップ！「新NISA」などの金融制度にも完全対応。さらに「証券口座やクレカ、銀行などの選び方」「超危険な金融商品リスト」など、新規内容も50ページ以上追加。実践しやすいお金の教養がてんこ盛りの一冊！",
            "image": "https://thumbnail.image.rakuten.co.jp/@0_mall/book/cabinet/3780/9784023323780_1_3.jpg?_ex=200x200",
            "itemUrl": "https://books.rakuten.co.jp/rb/18041936/?rafcid=wsc_b_bs_1077795699367532233",
            "price": 1650,
            "title": "改訂版　本当の自由を手に入れる　お金の大学",
        },
    ]
    shelves["積立安定型"] = [
        {
            "author": "両＠リベ大学長",
            "description": "142万部突破の『お金の大学』が超・パワーアップ！「新NISA」などの金融制度にも完全対応。さらに「証券口座やクレカ、銀行などの選び方」「超危険な金融商品リスト」など、新規内容も50ページ以上追加。実践しやすいお金の教養がてんこ盛りの一冊！",
            "image": "https://thumbnail.image.rakuten.co.jp/@0_mall/book/cabinet/3780/9784023323780_1_3.jpg?_ex=200x200",
            "itemUrl": "https://books.rakuten.co.jp/rb/18041936/?rafcid=wsc_b_bs_1077795699367532233",
            "price": 1650,
            "title": "改訂版　本当の自由を手に入れる　お金の大学",
        },
    ]

    my_books = shelves.get("私の本棚", [])
    shelf_books = shelves.get(name, [])

    return render_template(
        "bookshelf/shelf.html",
        shelf_name=name,
        shelves=shelves,
        my_shelf=my_books,
    )


# -----------------------------
# おすすめ
# -----------------------------
@bookshelf_bp.route("/recommend")
def recommend_books():
    history_json = request.args.get("history", "[]")
    history = json.loads(history_json)
    recommended = []
    all_books = []  # 実際の全書籍データをここでロードするとよい
    for h in history:
        for b in all_books:
            if b["title"] not in [x["title"] for x in history + recommended]:
                if (
                    h.get("tags")
                    and b.get("tags")
                    and any(tag in h["tags"].split() for tag in b["tags"].split())
                ):
                    recommended.append(b)
    return jsonify(recommended[:10])
