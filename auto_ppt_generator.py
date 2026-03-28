import os
import json
import requests
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

# ==========================================
# 1. 検索エンジンAPI（Serper等）でエリアの競合URLを大量取得する関数
# ==========================================
def search_competitors(area_query: str, limit: int = 2) -> list[str]:
    """
    指定されたエリアの「新築マンション」等のキーワードで検索し、
    上位の物件URLを取得する。（今回はデモ用にダミーURLを返します）
    ※ 本番運用ではGoogle Custom Search APIやSerper APIを利用します。
    """
    print(f"🔍 [{area_query}] 周辺の競合物件サイトを検索中...")
    # デモ用のダミー競合URLリスト（本来はAPIから取得）
    dummy_urls = [
        f"https://example.com/mansion/{area_query}_comp1",
        f"https://example.com/mansion/{area_query}_comp2"
    ]
    return dummy_urls[:limit]

# ==========================================
# 2. DifyのワークフローAPIを叩き、分析JSONを取得する関数
# ==========================================
def call_dify_workflow(my_url: str, comp_urls: list[str]) -> dict:
    """
    Difyで作成した「不動産Webサイト比較ワークフロー」のAPIエンドポイントを叩き、
    広告代理店視点での分析結果（JSONデータ）を取得する。
    """
    print("🤖 Difyワークフロー(AI)にURL群を送信し、高度な分析を実行中...")

    # --- 注意 ---
    # ここにDifyのAPIキーとURLを設定する必要があります。
    DIFY_API_KEY = os.environ.get("DIFY_API_KEY", "YOUR_DIFY_APP_API_KEY")
    DIFY_API_URL = "https://api.dify.ai/v1/workflows/run"

    comp_url_1 = comp_urls[0] if len(comp_urls) > 0 else ""
    comp_url_2 = comp_urls[1] if len(comp_urls) > 1 else ""

    payload = {
        "inputs": {
            "my_url": my_url,
            "comp_url_1": comp_url_1,
            "comp_url_2": comp_url_2
        },
        "response_mode": "blocking",
        "user": "auto_ppt_generator"
    }

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    # API呼び出し（実際のDify環境に合わせてコメントアウトを外して使用します）
    """
    try:
        response = requests.post(DIFY_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        # DifyのAnswerノードが出力したJSONテキストを取り出してパース
        answer_text = result.get('data', {}).get('outputs', {}).get('answer', '{}')

        # MarkdownのJSONコードブロック（```json ... ```）を削除
        if answer_text.startswith("```json"):
            answer_text = answer_text[7:]
        if answer_text.endswith("```"):
            answer_text = answer_text[:-3]

        return json.loads(answer_text)
    except Exception as e:
        print(f"❌ Dify APIエラー: {e}")
        return None
    """

    # ---------------------------------------------------------
    # デモ用モックデータ (APIが繋がっていない場合のテスト用)
    # ---------------------------------------------------------
    print("⚠️ Dify APIキーが未設定のため、デモ用モックデータを使用します。")
    return {
      "summary": {
        "my_site": "20代〜30代の単身者をメインターゲットとした、駅近の利便性とスタイリッシュなデザインを訴求するコンセプト。",
        "competitor1": "ファミリー層をターゲットにした、広々としたリビングと充実した共用施設をアピールする温かみのあるコンセプト。",
        "competitor2": "高価格帯の投資家やシニア層をターゲットとした、コンシェルジュサービスと高級感を前面に押し出したコンセプト。"
      },
      "comparison_scores": [
        {
          "category": "ファーストビューの訴求力",
          "my_site": {"score": 4, "reason": "単身者向けのスタイリッシュなCGが目を引き、キャッチコピーもシャープで印象に残る。"},
          "competitor1": {"score": 3, "reason": "ファミリー向けの画像は良いが、コピーが少し長くて読みにくい。"},
          "competitor2": {"score": 5, "reason": "高級ホテルのような動画背景とシンプルなコピーが非常に強いインパクトを与える。"}
        },
        {
          "category": "情報の整理とUI/UX",
          "my_site": {"score": 3, "reason": "スマホでの閲覧を前提とした縦長スクロールは良いが、設備詳細への導線が少し分かりにくい。"},
          "competitor1": {"score": 4, "reason": "間取りごとの比較機能があり、ユーザーが求める情報に辿り着きやすい。"},
          "competitor2": {"score": 3, "reason": "デザインを重視しすぎて、文字が小さく読みにくい箇所がある。"}
        },
        {
          "category": "ブランディングと世界観",
          "my_site": {"score": 4, "reason": "モノトーン基調の洗練されたトーン＆マナーがターゲット層と合致している。"},
          "competitor1": {"score": 3, "reason": "一般的なマンションサイトの枠を出ておらず、独自のブランドカラーが薄い。"},
          "competitor2": {"score": 5, "reason": "独自のフォントや高品質な写真を使用し、一貫したラグジュアリーな世界観を構築している。"}
        },
        {
          "category": "コンバージョンへの導線",
          "my_site": {"score": 2, "reason": "資料請求ボタンがページの最下部にしかなく、スクロール途中で離脱される可能性が高い。"},
          "competitor1": {"score": 4, "reason": "常に画面下部に追従する「来場予約」ボタンがあり、CVへの意識が高い。"},
          "competitor2": {"score": 3, "reason": "オンライン見学と来場予約の2つのボタンが並んでおり、少し迷わせるかもしれない。"}
        }
      ],
      "agency_analysis": {
        "strengths": "ターゲットを絞り込んだエッジの効いたデザインと、直感的に響くシャープなキャッチコピーは競合の中で際立っている。",
        "weaknesses": "「カッコよさ」を追求した結果、機能性（UI/UX）やCVへの導線設計がやや弱くなっており、興味を持ったユーザーを取りこぼしている可能性がある。"
      },
      "action_plans": [
        "画面下部に常に追従する「資料請求・来場予約」の固定ボタン（フローティングバナー）を設置し、CV率を改善する。",
        "ファーストビューの直下に「設備ハイライト」のセクションを追加し、デザインだけでなく機能的なメリットも早期に伝える。",
        "スマホ閲覧時のフォントサイズや行間を見直し、可読性を高める（特に物件概要などの詳細情報部分）。"
      ]
    }


# ==========================================
# 3. JSONデータからPPTXを自動生成する関数
# ==========================================
def generate_ppt_from_json(json_data: dict, output_filename: str = "Client_Presentation_AI.pptx"):
    """
    Difyから返されたJSONデータを受け取り、プロフェッショナルな
    PowerPoint（.pptx）資料を自動生成する。
    """
    print("📊 分析データ(JSON)を元に、クライアント提出用PowerPoint資料を生成中...")
    prs = Presentation()

    # --- 1. タイトルスライド ---
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "自社物件Webサイト 広告効果比較・分析レポート"
    slide.placeholders[1].text = "〜 UI/UX・ブランディング・CV導線に基づく改善提案 〜\n\nAI Marketing & Consulting"

    # --- 2. サイト・物件の全体概要スライド ---
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "各サイトの広告コンセプトとターゲット層"
    content = slide.placeholders[1].text_frame

    for site, summary in json_data.get("summary", {}).items():
        p = content.add_paragraph()
        site_name = "自社物件サイト" if site == "my_site" else f"競合サイト ({site})"
        p.text = f"【{site_name}】"
        p.level = 0
        p2 = content.add_paragraph()
        p2.text = summary
        p2.level = 1

    # --- 3. 広告代理店視点の評価スコア表スライド ---
    slide_layout = prs.slide_layouts[5] # Title Only
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "広告・Webマーケティング効果 比較スコア"

    # テーブルの作成 (行数=項目数+1, 列数=4)
    scores = json_data.get("comparison_scores", [])
    rows = len(scores) + 1
    cols = 4
    left = Inches(0.5)
    top = Inches(1.5)
    width = Inches(9)
    height = Inches(0.8 * rows)

    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    # ヘッダー行
    headers = ["評価項目", "自社物件", "競合物件1", "競合物件2"]
    for i, header_text in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header_text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.bold = True
            paragraph.alignment = PP_ALIGN.CENTER

    # データ行
    for r, score_data in enumerate(scores, start=1):
        table.cell(r, 0).text = score_data.get("category", "")
        for c, site in enumerate(["my_site", "competitor1", "competitor2"], start=1):
            site_data = score_data.get(site, {})
            score = site_data.get("score", "-")
            reason = site_data.get("reason", "")
            # スコアは★で表現
            stars = "★" * int(score) if isinstance(score, int) else str(score)
            cell_text = f"スコア: {score}/5\n{stars}\n{reason}"
            table.cell(r, c).text = cell_text
            # フォントサイズ調整
            for paragraph in table.cell(r, c).text_frame.paragraphs:
                paragraph.font.size = Pt(10)

    # --- 4. プロの視点：強みと弱みスライド ---
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "代理店アナリストの総評（強みと弱み）"
    content = slide.placeholders[1].text_frame

    analysis = json_data.get("agency_analysis", {})

    p = content.add_paragraph()
    p.text = "🔴 自社サイトの強み（訴求ポイント）"
    p.font.bold = True
    p2 = content.add_paragraph()
    p2.text = analysis.get("strengths", "")
    p2.level = 1

    p3 = content.add_paragraph()
    p3.text = "\n🔵 自社サイトの弱み（CV取りこぼしの要因）"
    p3.font.bold = True
    p4 = content.add_paragraph()
    p4.text = analysis.get("weaknesses", "")
    p4.level = 1

    # --- 5. アクションプラン（改善提案）スライド ---
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "サイト改善・CV最大化へのアクションプラン"
    content = slide.placeholders[1].text_frame

    plans = json_data.get("action_plans", [])
    for i, plan in enumerate(plans, start=1):
        p = content.add_paragraph()
        p.text = f"提案 {i}:"
        p.font.bold = True
        p.level = 0
        p2 = content.add_paragraph()
        p2.text = plan
        p2.level = 1

    prs.save(output_filename)
    print(f"✅ クライアント提出用資料の生成が完了しました！ -> {output_filename}")


# ==========================================
# メイン処理 (システム連携の全体像)
# ==========================================
if __name__ == "__main__":
    print("="*50)
    print("🏢 不動産Webマーケティング自動分析システム起動")
    print("="*50)

    # 1. 自社URLの設定と、エリア名に基づく競合検索（今回は仮設定）
    my_property_url = "https://example.com/my-mansion"
    target_area = "品川区 新築マンション"

    # エリア検索で競合URLを自動取得（ナレッジ収集の第一歩）
    competitor_urls = search_competitors(target_area, limit=2)

    # 2. 取得したURL群をDify（AIワークフロー）に投げて、高度な分析JSONを取得
    analysis_json = call_dify_workflow(my_property_url, competitor_urls)

    # 3. Difyから得たJSON構造体から、綺麗なPowerPoint資料を全自動生成
    if analysis_json:
        generate_ppt_from_json(analysis_json, "自動生成_不動産Web比較提案書.pptx")
    else:
        print("❌ 分析データの取得に失敗したため、資料作成を中止しました。")
