import os
import random
import requests
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
import pdfkit
from dotenv import load_dotenv

# Load environment variables if any (like FACEBOOK_ACCESS_TOKEN for future use)
load_dotenv()

def fetch_real_facebook_posts(access_token, limit=50):
    """
    Fetches real posts and photos from the user's Facebook account using the Graph API.
    Requires a valid User Access Token with 'user_posts' and 'user_photos' permissions.
    """
    print("🌐 Facebook Graph APIから実際のデータを取得しています...")
    # Get the user's feed, focusing on posts with photos
    url = f"https://graph.facebook.com/v19.0/me/feed"
    params = {
        'fields': 'id,message,created_time,full_picture',
        'access_token': access_token,
        'limit': limit
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        posts = []
        for item in data.get('data', []):
            # Only include posts that have a picture for the photobook
            if 'full_picture' in item:
                created_time = datetime.strptime(item['created_time'], "%Y-%m-%dT%H:%M:%S%z")

                post = {
                    "id": item.get('id'),
                    "text": item.get('message', ''), # Some photo posts have no text
                    "image_url": item['full_picture'],
                    "created_time_obj": created_time, # Store for accurate sorting
                }
                posts.append(post)

        # Sort posts chronologically (oldest first for a book) using the exact datetime object
        posts.sort(key=lambda x: x['created_time_obj'])

        # Format the date string for display after sorting
        for post in posts:
            post['date'] = post['created_time_obj'].strftime("%Y年%m月%d日")

        print(f"✅ APIから {len(posts)} 件の画像付き投稿を取得しました。")
        return posts

    except requests.exceptions.RequestException as e:
        print(f"❌ Facebook Graph APIからのデータ取得に失敗しました: {e}")
        print("   アクセストークンが無効か、権限(user_posts)が不足している可能性があります。")
        return []

def generate_mock_posts(num_posts):
    """
    Generates dummy data representing Facebook posts (photos and text).
    This is used as a fallback if no valid Facebook Access Token is provided.
    """
    sample_texts = [
        "今日は素晴らしい天気ですね！散歩に行ってきました。最高のリフレッシュになりました！ #散歩 #快晴",
        "美味しいランチをいただきました。また来たいお店です！😋 #ランチ #グルメ",
        "新しいプロジェクトが始まりました。頑張るぞ！💪 #仕事 #スタート",
        "週末は家族で旅行。綺麗な景色に癒やされました。 #旅行 #家族",
        "ずっと欲しかった本をついにゲット。今夜から読むのが楽しみ！📖 #読書 #休日",
        "久しぶりに友人と再会。話が尽きなくて楽しい時間を過ごせました。✨",
        "少し疲れたので、コーヒーブレイク。リラックスタイム大事☕",
        "初めての登山。頂上からの景色は圧巻でした！ #登山 #アウトドア",
        "今日は何もせず家でのんびり。こういう日も必要ですね。🏠",
        "夕焼けがとても綺麗だったので思わず写真を撮りました。 #夕焼け #空",
    ]

    base_image_url = "https://picsum.photos/seed/{}/800/600"
    posts = []
    base_date = datetime.now()

    for i in range(num_posts):
        # We also want time to be somewhat random for accurate mock sorting
        post_date = base_date - timedelta(days=random.randint(1, 100), hours=random.randint(1, 23), minutes=random.randint(1, 59))
        post = {
            "id": f"post_{i+1}",
            "text": random.choice(sample_texts),
            "image_url": base_image_url.format(random.randint(1, 1000)),
            "created_time_obj": post_date,
        }
        posts.append(post)

    posts.sort(key=lambda x: x['created_time_obj'])
    for post in posts:
        post['date'] = post['created_time_obj'].strftime("%Y年%m月%d日")

    return posts

def get_allowed_page_counts():
    """Returns the allowed total page counts for the photobook (24 to 48, step 4)."""
    return list(range(24, 49, 4))

def render_pdf(posts, target_page_count, output_filename="sample_book.pdf"):
    """
    Renders the given posts into a PDF using Jinja2 and wkhtmltopdf.
    """
    if not posts:
        print("❌ 投稿データが空のため、PDFを生成できません。")
        return

    allowed_counts = get_allowed_page_counts()
    if target_page_count not in allowed_counts:
        raise ValueError(f"指定されたページ数 {target_page_count} は無効です。選択可能なページ数: {allowed_counts}")

    print(f"📖 {target_page_count}ページのフォトブックを生成します...")

    # 1 Cover page, (target_page_count - 1) Post pages
    required_post_pages = target_page_count - 1

    if len(posts) > required_post_pages:
        print(f"⚠️ 投稿が多すぎます。最初の {required_post_pages} 件のみを使用します。")
        posts = posts[:required_post_pages]
    elif len(posts) < required_post_pages:
        shortfall = required_post_pages - len(posts)
        print(f"⚠️ 投稿が {shortfall} 件不足しています。ダミーページで埋めます。")
        for i in range(shortfall):
            posts.append({
                "text": "--- No Data ---",
                "image_url": "https://via.placeholder.com/800x600.png?text=Blank+Page",
                "date": ""
            })

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('book_template.html')

    html_content = template.render(
        title="My Special Memories",
        date=datetime.now().strftime("%Y年%m月"),
        posts=posts
    )

    options = {
        'page-size': 'A4',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }

    print("⏳ PDFへ変換中 (この処理には数秒かかります)...")
    try:
        pdfkit.from_string(html_content, output_filename, options=options)
        print(f"✅ フォトブックの生成が完了しました！ -> {output_filename}")
        print(f"   (全 {target_page_count} ページ構成：表紙1枚 + 本文{required_post_pages}枚)")
    except Exception as e:
        print(f"❌ PDFの生成中にエラーが発生しました: {e}")

if __name__ == "__main__":
    print("=== Facebook Photo Book Maker ===")

    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    if access_token:
        print("🔑 FACEBOOK_ACCESS_TOKEN が見つかりました。実際のデータを取得します。")
        # Try to fetch 50 recent posts with photos
        post_data = fetch_real_facebook_posts(access_token, limit=50)

        if not post_data:
            print("⚠️ 実際のデータが取得できなかったため、フォールバックとしてモックデータを使用します。")
            post_data = generate_mock_posts(35)
    else:
        print("⚠️ FACEBOOK_ACCESS_TOKEN が設定されていません。")
        print("   ※ 自分のデータで生成するには、.envファイルにトークンを設定してください。")
        print("   ※ テストのためモックデータを使用します。")
        post_data = generate_mock_posts(35)

    # ページ数は２４ページから48Pまで４ページ刻みで選べます
    # 初期値として24ページを設定
    target_pages = 24

    render_pdf(post_data, target_pages, output_filename="my_facebook_book.pdf")

    print("\n💡 ヒント:")
    print("1. 生成されたPDFのページ数を変更したい場合は、コード内の `target_pages` の値を 28, 32, 36などに変更してください。")
    print("2. 自分のデータを使うには、Meta for Developersでアプリを作成し、Graph APIエクスプローラーから")
    print("   'user_posts' および 'user_photos' 権限を持つアクセストークンを取得して、.env に保存してください。")
    print("   例：FACEBOOK_ACCESS_TOKEN=EAACxxxx...")