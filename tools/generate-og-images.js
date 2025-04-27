const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

// サンプルデータのスラッグ
const slugs = [
  'demo-takahiro-anno-2024',
  'demo-ryosuke-idei-2024'
];

// グラフをキャプチャする関数
async function captureGraph(slug) {
  console.log(`Capturing graph for ${slug}...`);
  
  // ブラウザを起動
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // ビューポートサイズを設定
    await page.setViewport({
      width: 1200,
      height: 630,
      deviceScaleFactor: 2 // 高解像度でキャプチャ
    });
    
    // ページに移動
    await page.goto(`http://localhost:3000/${slug}`, {
      waitUntil: 'networkidle0',
      timeout: 30000
    });
    
    // グラフ要素を待機
    await page.waitForSelector('.sankey-chart', { timeout: 10000 })
      .catch(() => console.log('Sankey chart not found, trying alternative selector...'));
    
    // グラフ要素を取得
    const graphElement = await page.$('.sankey-chart') || 
                         await page.$('svg') || 
                         await page.$('.nivo-sankey');
    
    if (!graphElement) {
      console.error(`Graph element not found for ${slug}`);
      return;
    }

    // グラフ要素のサイズを取得
    const boundingBox = await graphElement.boundingBox();
    if (!boundingBox) {
      console.error(`Could not get bounding box for ${slug}`);
      return;
    }

    // 余白を追加
    const padding = 40;
    const width = Math.ceil(boundingBox.width + padding * 2);
    const height = Math.ceil(boundingBox.height + padding * 2);
    
    // スクリーンショットを撮る
    const outputPath = path.join(__dirname, '../public/ogp', `${slug}.png`);
    await graphElement.screenshot({
      path: outputPath,
      omitBackground: true
    });
    
    console.log(`Generated OGP image: ${outputPath}`);
  } catch (error) {
    console.error(`Error capturing graph for ${slug}:`, error);
  } finally {
    await browser.close();
  }
}

// メイン処理
async function main() {
  // 出力ディレクトリを作成
  const outputDir = path.join(__dirname, '../public/ogp');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // 各スラッグのグラフをキャプチャ
  for (const slug of slugs) {
    await captureGraph(slug);
  }
  
  console.log('All OGP images generated successfully!');
}

// スクリプト実行
main().catch(console.error);

