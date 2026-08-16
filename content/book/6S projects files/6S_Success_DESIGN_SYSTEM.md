# 6S Success — Design System Reference
*(Project knowledge. This is the single source of truth for the book's look so every chapter's `final.html` is identical in styling.)*

## Design intent
A premium illustrated field guide / workbook. Warm, friendly, confident, modern. Not a factory manual, not a sterile minimalist showroom. Visual ratio target across the book: 55 to 65% text, 35 to 45% visuals. Spend boldness on the one signature device (the friction meter); keep everything else quiet and disciplined.

## Palette (named hex)
- Paper background `#F7F2E9`
- Panel / card `#FBF7EF`
- Ink (warm near-black) `#2B2622`
- Soft text `#6A625A`
- Terracotta (headings, accents) `#BC4B2A`
- Honey (warm highlights, art notes) `#DDA63A`
- Slate (data, friction meter cool zone) `#3C5A6B`
- Calm green (calm-dots) `#6E8B5B`
- Friction spark (alert) `#CB4B36`
- Rule / divider `#E2D8C4` and `#D9CDB8`
- Soft wood/fill for furniture in art `#E7C58B`

## Type
- Display / headings: **Fraunces** (weights 400/500/600/900). Fallback Georgia, serif.
- Body: **Newsreader** (book serif). Fallback Georgia, Times, serif.
- Labels / captions / data: clean sans (Inter / system-ui stack).
- Load via Google Fonts; always keep serif/sans fallbacks in case fonts do not load.

## Signature device: the friction meter
A half-circle gauge dialing from CALM (green, left) through honey to FRICTION (red, right), with a needle. It recurs as a chapter-close ritual showing progress through the book. Be honest with it: move it when the chapter moved objects, hold it steady when the chapter built understanding only.

## Visual vocabulary (use consistently)
- **Green calm-dots** (`#6E8B5B`) mark places where something has a clear home / low friction.
- **Red friction-sparks** (`#CB4B36`, small star/cross bursts) mark snag points.
- All hand-drawn art: warm line-and-flat-color style, consistent stroke width (~3px), friendly but not childish, rounded corners on furniture.
- Infographics and diagrams: build as real inline SVG (charts, mappings, loops, timelines). Photography and full hand-drawn spreads: render as styled for-position figures and add an art note: `◆ Final book: ...`.

## Reusable stylesheet (paste into each chapter's final.html `<head>`)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>
:root{
  --paper:#F7F2E9; --panel:#FBF7EF; --ink:#2B2622; --soft:#6A625A;
  --terra:#BC4B2A; --honey:#DDA63A; --slate:#3C5A6B;
  --green:#6E8B5B; --spark:#CB4B36; --rule:#E2D8C4; --rule2:#D9CDB8;
  --sans:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  --serif:"Newsreader",Georgia,"Times New Roman",serif;
  --display:"Fraunces",Georgia,serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0; background:var(--paper); color:var(--ink); font-family:var(--serif); font-size:19px; line-height:1.62; font-weight:400;}
.book{max-width:1000px; margin:0 auto; padding:0 28px 120px;}
.prose > p,.prose > .what,.prose > h2,.prose > h3,.prose > .pull,.prose > ul{max-width:664px; margin-left:auto; margin-right:auto;}
.prose > p{margin:0 auto 1.05em}
.eyebrow{font-family:var(--sans); font-size:12.5px; letter-spacing:.22em; text-transform:uppercase; color:var(--terra); font-weight:600; margin:0;}
.masthead{padding:56px 0 8px; text-align:left; max-width:664px; margin:0 auto}
.chno{font-family:var(--display); font-weight:900; font-size:15px; letter-spacing:.06em; color:var(--slate); text-transform:uppercase; margin:0 0 14px;}
h1.title{font-family:var(--display); font-weight:600; font-size:clamp(38px,7vw,64px); line-height:1.02; letter-spacing:-.015em; margin:.1em 0 .25em; color:var(--ink);}
.subtitle{font-family:var(--serif); font-style:italic; color:var(--soft); font-size:clamp(18px,2.5vw,22px); margin:0 0 6px; max-width:560px;}
h2{font-family:var(--display); font-weight:600; font-size:clamp(25px,3.4vw,32px); line-height:1.1; letter-spacing:-.01em; margin:2.4em auto .55em; color:var(--ink);}
h2 .kick{display:block; font-family:var(--sans); font-size:12px; font-weight:600; letter-spacing:.2em; text-transform:uppercase; color:var(--terra); margin-bottom:.5em;}
.opening > p:first-of-type::first-letter{font-family:var(--display); font-weight:900; color:var(--terra); float:left; font-size:4.5em; line-height:.78; padding:.04em .09em 0 0; margin-top:.02em;}
.lead{font-size:1.06em}
em{font-style:italic} strong{font-weight:600}
.pull{font-family:var(--display); font-weight:500; font-size:clamp(22px,3.4vw,29px); line-height:1.24; color:var(--slate); border-top:2px solid var(--rule2); border-bottom:2px solid var(--rule2); padding:.7em 0; margin:1.8em auto; text-align:left;}
.what{background:var(--panel); border:1px solid var(--rule); border-radius:14px; padding:26px 30px 22px; margin:2em auto 1.4em;}
.what h4{font-family:var(--sans); font-size:12px; letter-spacing:.2em; text-transform:uppercase; color:var(--terra); font-weight:700; margin:0 0 14px;}
.what ul{list-style:none; margin:0; padding:0; max-width:none}
.what li{position:relative; padding-left:30px; margin:.5em 0; font-size:17.5px; line-height:1.5;}
.what li::before{content:""; position:absolute; left:4px; top:.55em; width:9px; height:9px; background:var(--green); border-radius:50%;}
.callout{border:1px solid var(--rule); border-left:5px solid var(--terra); background:var(--panel); border-radius:0 12px 12px 0; padding:18px 22px; margin:1.7em auto; max-width:664px;}
.callout .lbl{font-family:var(--sans); font-size:11.5px; font-weight:700; letter-spacing:.16em; text-transform:uppercase; color:var(--terra); display:flex; align-items:center; gap:8px; margin-bottom:7px;}
.callout p{margin:0; font-size:17px; line-height:1.52}
.callout.tip{border-left-color:var(--slate)} .callout.tip .lbl{color:var(--slate)}
.callout.win{border-left-color:var(--green)} .callout.win .lbl{color:var(--green)}
.callout.family{border-left-color:var(--honey)} .callout.family .lbl{color:#B5811E}
.callout.mistake{border-left-color:var(--spark)} .callout.mistake .lbl{color:var(--spark)}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block;background:currentColor}
figure{margin:2.4em 0;}
figure svg{display:block;width:100%;height:auto;border-radius:12px}
.figframe{border:1px solid var(--rule);background:var(--panel);border-radius:14px;padding:14px;box-shadow:0 1px 0 var(--rule2)}
figcaption{font-family:var(--sans); font-size:14.5px; line-height:1.5; color:var(--soft); margin:14px 4px 2px; max-width:760px;}
figcaption b{color:var(--ink);font-weight:600}
.artnote{display:block; font-family:var(--sans); font-size:12px; color:var(--honey); letter-spacing:.04em; margin-top:6px; font-style:normal;}
.artnote::before{content:"\25C6 "; color:var(--honey)}
.defbox{background:var(--panel);border:2px solid var(--slate);border-radius:14px;padding:24px 28px;max-width:664px;margin:1.8em auto}
.defbox .lbl{font-family:var(--sans);font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--slate);font-weight:700;margin-bottom:10px}
.defbox p{margin:0;font-family:var(--display);font-weight:500;font-size:22px;line-height:1.3;color:var(--ink)}
.checklist{max-width:664px;margin:1.5em auto;background:var(--panel);border:1px dashed var(--rule2);border-radius:12px;padding:22px 26px}
.checklist h4{font-family:var(--sans);font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--slate);font-weight:700;margin:0 0 12px}
.checklist ul{list-style:none;margin:0;padding:0}
.checklist li{position:relative;padding-left:34px;margin:.55em 0;font-size:17px;line-height:1.45}
.checklist li::before{content:"";position:absolute;left:0;top:.05em;width:19px;height:19px;border:2px solid var(--slate);border-radius:5px}
.idea{background:var(--ink); color:var(--paper); border-radius:16px; padding:30px 34px; max-width:664px; margin:2.2em auto;}
.idea .lbl{font-family:var(--sans);font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--honey);font-weight:700;margin-bottom:10px}
.idea p{margin:0;font-family:var(--display);font-weight:500;font-size:23px;line-height:1.3}
.next{max-width:664px;margin:2em auto 0;border-top:2px solid var(--rule2);padding-top:18px;}
.next .lbl{font-family:var(--sans);font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--terra);font-weight:700}
.next p{margin:.4em 0 0;color:var(--soft)}
.next b{color:var(--ink)}
@media (max-width:640px){ body{font-size:17.5px} .masthead{padding:40px 0 4px} }
@media print{ body{background:#fff} .figframe{box-shadow:none} }
</style>
```

## Page skeleton
```html
<main class="book">
  <header class="masthead">
    <p class="chno">Part One · Discovering 6S</p>
    <p class="eyebrow">Chapter Two</p>
    <h1 class="title">Chapter Title</h1>
    <p class="subtitle">One-line italic promise.</p>
  </header>
  <figure class="figframe"> ...opener visual... <figcaption>...</figcaption></figure>
  <div class="prose">
    <section class="opening"><p class="lead">...</p> ...drop-cap opening...</section>
    <aside class="callout tip"><div class="lbl"><span class="dot"></span>6S Tip</div><p>...</p></aside>
    <div class="what"><h4>In this chapter</h4><ul><li>...</li></ul></div>
    <h2><span class="kick">Eyebrow</span>Section Title</h2>
    <p>...</p>
    <figure><div class="figframe"><svg>...</svg></div><figcaption>...</figcaption></figure>
    ...
    <div class="idea"><div class="lbl">One Idea to Keep</div><p>...</p></div>
    <figure>...friction meter...</figure>
    <div class="next"><div class="lbl">Next</div><p><b>Chapter N · Title.</b> teaser</p></div>
  </div>
</main>
```

## Quality floor (every chapter)
Zero em dashes. Responsive to mobile. Good contrast. Figures balanced with prose (never stack visuals back to back without text between). Validate the HTML parses and `<figure>`/`</figure>` are balanced before delivering.
