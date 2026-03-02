from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def create_presentation():
    prs = Presentation()

    # 1. タイトルスライド
    slide_layout = prs.slide_layouts[0] # 0: Title Slide
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "AI 不動産コンサルタント\nWebサイト比較エージェント"
    subtitle.text = "自社と競合のマンション物件サイトを自動分析\n\nDifyを活用した導入・活用のご案内"

    # 2. 課題と解決策スライド
    slide_layout = prs.slide_layouts[1] # 1: Title and Content
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "背景と課題 / AIによる解決策"

    content = slide.placeholders[1].text_frame
    content.text = "【現状の課題】"
    p = content.add_paragraph()
    p.text = "競合物件のリサーチ・比較表作成に膨大な時間がかかっている"
    p.level = 1
    p = content.add_paragraph()
    p.text = "担当者によって分析の視点や質にバラつきがある"
    p.level = 1

    p = content.add_paragraph()
    p.text = "\n【AIエージェントによる解決策】"
    p.level = 0
    p = content.add_paragraph()
    p.text = "URLを入力するだけで、瞬時に情報を収集・比較"
    p.level = 1
    p = content.add_paragraph()
    p.text = "プロの「不動産コンサルタント」の視点で一貫した分析を提供"
    p.level = 1

    # 3. エージェントの特徴スライド
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "システムの主な特徴"

    content = slide.placeholders[1].text_frame
    content.text = "Difyを活用した最新のAIエージェント"

    p = content.add_paragraph()
    p.text = "Webスクレイピングの完全自動化"
    p.level = 1
    p2 = content.add_paragraph()
    p2.text = "指定された複数URLをクローラーが自動で巡回・テキスト抽出"
    p2.level = 2

    p = content.add_paragraph()
    p.text = "不動産業界に特化した分析プロンプト"
    p.level = 1
    p2 = content.add_paragraph()
    p2.text = "立地、価格、間取り、設備、共用施設など、顧客が重視する項目を網羅"
    p2.level = 2

    p = content.add_paragraph()
    p.text = "構造化されたレポート出力"
    p.level = 1
    p2 = content.add_paragraph()
    p2.text = "比較表（Markdownテーブル形式）による視覚的なわかりやすさ"
    p2.level = 2
    p2 = content.add_paragraph()
    p2.text = "強み・弱み分析に基づく具体的なアクションプランの提示"
    p2.level = 2

    # 4. 利用イメージスライド
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "利用イメージと出力結果"

    content = slide.placeholders[1].text_frame
    content.text = "チャット形式で簡単操作"

    p = content.add_paragraph()
    p.text = "【入力例】"
    p.level = 1
    p2 = content.add_paragraph()
    p2.text = "「自社物件: https://... / 競合物件1: https://... を比較して」と送信するだけ。"
    p2.level = 2

    p = content.add_paragraph()
    p.text = "【出力されるレポート構成】"
    p.level = 1
    p2 = content.add_paragraph()
    p2.text = "1. サイト・物件の全体概要（コンセプト、ターゲット層）"
    p2.level = 2
    p2 = content.add_paragraph()
    p2.text = "2. 物件比較サマリー（一覧表）"
    p2.level = 2
    p2 = content.add_paragraph()
    p2.text = "3. 自社物件の強みと弱みの分析（SWOT的視点）"
    p2.level = 2
    p2 = content.add_paragraph()
    p2.text = "4. サイト改善・販売促進アクションプランの提案"
    p2.level = 2

    # 5. 今後の展開スライド
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "Difyへの導入方法"

    content = slide.placeholders[1].text_frame
    content.text = "DSLファイルのインポートで即日利用可能"

    p = content.add_paragraph()
    p.text = "1. 設定ファイル（website_comparison_agent.yml）を取得"
    p.level = 1
    p = content.add_paragraph()
    p.text = "2. Difyダッシュボードの「DSLをインポート」からアップロード"
    p.level = 1
    p = content.add_paragraph()
    p.text = "3. そのまま「プレビュー」や「公開」から利用開始可能"
    p.level = 1
    p = content.add_paragraph()
    p.text = "※社内知識データベース（PDF図面集や価格表など）を追加学習させることも将来的に拡張可能"
    p.level = 1

    prs.save("Webサイト比較エージェント_提案資料.pptx")
    print("Presentation created successfully.")

if __name__ == "__main__":
    create_presentation()
