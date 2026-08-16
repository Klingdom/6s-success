# -*- coding: utf-8 -*-
"""Build the 6S Success Home Micro Zones MVP Beta PWA (self-contained mobile web app)."""
import io, json, os

SCRATCH = r"C:\Users\philk\AppData\Local\Temp\claude\C--Users-philk-6s-success\98389a9c-eed9-4e7a-a8f6-53e8ba8db3f8\scratchpad"
OUTDIR = r"C:\Users\philk\Desktop\6S-Home-MicroZones-MVP-Beta\app"

data = json.load(io.open(SCRATCH + r"\app_data.json", encoding="utf-8"))
DATA_JSON = json.dumps(data, ensure_ascii=False)

# ---------------- app.js (the whole application logic + UI) ----------------
APP_JS = r"""
/* ================= 6S Success Home Micro Zones - MVP Beta =================
   Self-contained mobile web app. On-device storage (localStorage + IndexedDB),
   camera capture, and a CONFIGURABLE AI endpoint (Settings). Degrades to the
   static per-zone plan when no AI endpoint is set. Logic ported from the v2.4
   artifact; storage and AI transport rebuilt to run off the artifact host. */

const DATA = __DATA__;
const ROOMS = DATA.rooms, PRODUCTS = DATA.products;
const MAX_PHOTOS = 6, MAX_CHARS = 240000;

/* ---- 6S constants (ported) ---- */
const STEP_C = ["#a8452f","#b8862b","#3f6647","#16395f","#6b4f8a","#3d6d74"];
const ABBR = ["SOR","STR","SHI","SAF","STD","SUS"];
const STEPS = [
 {k:"Sort",tag:"Separate the necessary from the unnecessary",
  meta:"Empty the zone of everything that does not serve its function. Decide fast: keep, relocate, donate, recycle, or discard. Undecided items go to a dated holding bin, never back into the zone.",
  needs:z=>`Trash, recycling, and donation containers; a dated holding bin for true maybes. Typical contents here: ${z.i}.`,
  done:z=>`${z.n} holds only items that serve its function, ${z.f.toLowerCase()}. Everything else is routed out, relocated, or time-boxed.`},
 {k:"Straighten",tag:"A home for everything, chosen by how it is used",
  meta:"Give every kept item one visible, reachable home. Place by frequency and sequence of use: daily items at hand height, occasional items higher or lower, heavy items always low.",
  needs:z=>z.s?`Kept items plus storage controls such as ${z.s}.`:"Kept items and your existing storage.",
  done:z=>z.s?`Every kept item has a defined, reachable home using ${z.s}; retrieval and return take one motion.`:"Every kept item has a defined, reachable home; retrieval and return take one motion."},
 {k:"Shine",tag:"Clean to inspect, not just to impress",
  meta:"Clean top-down and back-to-front: surfaces, containers, fixtures, and the items themselves. Treat cleaning as inspection: note wear, damage, drips, and leaks as you go.",
  needs:()=>"Cleaning supplies matched to the surfaces, cloths, and a vacuum or brush.",
  done:()=>"Surfaces, containers, fixtures, and retained items are clean, dry, inspected, and ready for use."},
 {k:"Safety",tag:"The step that protects everything else",
  meta:"Walk the zone as an auditor: clear egress, stable stacks, secured chemicals, sound cords, dry floors, safe reach and lift. Fix what you can now; tag and schedule what you cannot.",
  needs:z=>z.h?`A cleared zone and a hazard eye for: ${z.h}.`:"A cleared zone and a careful hazard walk.",
  done:z=>z.h?`Hazards corrected or controlled: ${z.h}; access and required clearances restored.`:"Hazards corrected or controlled; access and required clearances restored."},
 {k:"Standardize",tag:"Make the right state obvious at a glance",
  meta:"Lock in the arrangement so anyone can repeat it without memory: labels, quantity limits, a reference photo, and a one-glance definition of done.",
  needs:z=>`Labels, quantity limits, and your after photo as the reference standard${z.s?`; storage method: ${z.s}`:""}.`,
  done:z=>`The target state is documented and visible: ${z.g}`},
 {k:"Sustain",tag:"Design the habit, do not rely on willpower",
  meta:"Build the habit that keeps it done: a named owner, a reset trigger tied to an existing routine, and a two-minute audit on a set cadence.",
  needs:()=>"A named owner, a reset trigger tied to an existing routine, and a two-minute audit cadence.",
  done:z=>`A simple reset-and-review routine protects the target state: ${z.g}`},
];
const LEVELS={C:"Core",R:"Recommended",D:"Conditional"};
const PICKS=[["b","Top name brand"],["g","Best generic"],["v","Best overall"]];
const VERDICT={relocate:{c:"#16395f",label:"Relocate"},donate:{c:"#b8862b",label:"Donate"},discard:{c:"#a8452f",label:"Discard"},"keep-maybe":{c:"#6b4f8a",label:"Holding bin"}};
const midCost=p=>Math.round((p.lo+p.hi)/2);

/* ---- content engine (ported verbatim in logic) ---- */
const zoneText=z=>(z.n+" "+z.i+" "+z.f+" "+(z.s||"")).toLowerCase();
const has=(z,...keys)=>{const t=zoneText(z);return keys.some(k=>t.includes(k));};
const fnLower=z=>z.f?z.f[0].toLowerCase()+z.f.slice(1):"its function";
function stepInputs(zone,stepIdx,gear){
  const hits=[];
  for(const e of (zone.pr||[])){const p=PRODUCTS[e[0]];
    if(p.ph.includes(String(stepIdx))) hits.push({i:e[0],n:p.n,own:gear.has(e[0]),lvl:e[1],use:e[2]});}
  const order={C:0,R:1,D:2};
  hits.sort((a,b)=>(order[a.lvl]-order[b.lvl])||(b.own-a.own)||a.n.localeCompare(b.n));
  return hits.slice(0,10);
}
function subSteps(zone,i){
  const out=[];
  if(i===0){
    out.push("Stage your routing set at the zone's mouth: keep, relocate, donate, recycle, trash, plus a dated holding bin for true maybes.");
    out.push(has(zone,"drawer")?"Pull the drawer fully out if you can and empty it completely onto a clear surface. Sorting in place hides the bottom layer.":"Empty the zone completely onto a clear staging surface, working left to right so nothing gets skipped.");
    out.push(`Run ten-second verdicts: does it serve ${fnLower(zone)}? Only clear yeses go in the keep pile.`);
    out.push(`Expect to handle: ${zone.i}. Duplicates: keep the best one, route the rest.`);
    if(has(zone,"food","pantry","spice","snack","refrigerator","canned","dry goods","baking")) out.push("Check every date. Expired food is trash, no negotiating, no sniff tests on the fence-sitters.");
    if(has(zone,"medicine","cosmetic","vanity","sunscreen","makeup")) out.push("Check expiry and open-jar ages (most cosmetics 6 to 24 months). Expired medicines go to a take-back program, never the toilet.");
    if(has(zone,"chemical","cleaner","detergent","paint","solvent","finishing")) out.push("Chemicals stay in original containers only; anything unlabeled, crusted, or mystery-mixed gets set aside for hazardous-waste disposal.");
    out.push("Close the loop now: donation bag to the car, relocations delivered, trash out. Nothing waits in a pile.");
  }
  if(i===1){
    out.push("Group the keepers by function, then by frequency: daily, weekly, occasional or seasonal.");
    out.push("Assign homes by ergonomics: daily items at hand height, weekly at knee-to-shoulder, occasional high or deep, and heavy always low.");
    if(zone.s) out.push(`Deploy the zone's controls: ${zone.s}.`);
    if(has(zone,"closet","hanging","coat","clothing","dresser")) out.push("Uniform hangers, one direction; fold flat storage vertically (file-fold) so every item is visible from above.");
    if(has(zone,"garage","workshop","tool","shed","wall")) out.push("Take storage vertical: rails, hooks, and pegboard before shelves. The floor keeps only wheeled and parked things.");
    out.push("Run the one-motion test: retrieve and return each daily item without moving anything else. If you cannot, re-place it.");
    out.push("Face labels out, handles toward the hand, nothing stacked past easy reach of the bottom item.");
  }
  if(i===2){
    if(has(zone,"shower","tub")) out.push("Spray tub-and-tile cleaner FIRST and give it a full 5-minute dwell. Let chemistry do the scrubbing while you work elsewhere.");
    out.push("Dry soil first: dust and vacuum top-down, back-to-front. Crumbs and grit before any wet chemistry.");
    if(has(zone,"cooking","stove","oven","grill","range")) out.push("Degrease before you sanitize. Warm soapy water or degreaser first, because sanitizer cannot penetrate grease film; then disinfect food-contact surfaces with full label dwell time.");
    if(has(zone,"sink","faucet")) out.push("Sink: apply cleaner and let it dwell 3 to 5 minutes, scrub, rinse, then DRY the basin and buff the faucet. Dry chrome does not water-spot.");
    if(has(zone,"toilet")) out.push("Bowl cleaner under the rim first; while it dwells, disinfect tank, seat, hinges, and base top-down. Brush the bowl last; flush lid-down.");
    if(has(zone,"shower","tub")) out.push("Now scrub: grout lines with a brush, fixtures with non-scratch pads, rinse top-down, and squeegee every glass and tile surface dry.");
    if(has(zone,"mirror","glass","window","display cabinet")) out.push("Glass two-cloth method: spray cleaner onto the cloth (never the surface near electronics), wipe in an S-pattern, buff with a second dry microfiber.");
    if(has(zone,"refrigerator")) out.push("Work shelf by shelf: remove, wash in warm soapy water, dry fully, reload. Never hot water on cold glass, thermal shock cracks shelves.");
    if(has(zone,"washer","dryer")) out.push("Machine care: scrub the door gasket folds and detergent drawer, clear the lint path, and run a hot maintenance wash monthly.");
    if(has(zone,"sofa","cushion","upholster","mattress","bed and","blanket","rug")) out.push("Fabric: vacuum seams and crevices with the upholstery tool, spot-treat stains from the outside in, and let everything dry completely before reassembly.");
    if(has(zone,"wood","dining table","dresser","bookshel","nightstand","sideboard")) out.push("Wood: wipe with a barely-damp microfiber and dry immediately. Standing moisture is wood's enemy; condition quarterly so spills bead.");
    if(has(zone,"media","electronic","device","charging","computer","printer","desk")) out.push("Electronics: power down; spray screen cleaner on the cloth, never the device; compressed air for keyboards, vents, and ports.");
    if(has(zone,"floor","path","mat","stair","landing zone","garage")) out.push("Floors last: vacuum edges and corners first, then clean with a floor-matched product in overlapping strokes, working toward the exit.");
    if(!has(zone,"shower","tub","toilet","sink","refrigerator","washer")) out.push("Wipe remaining surfaces with multi-surface cleaner in an S-pattern, no circles, they redeposit soil; flip to the dry side to finish.");
    out.push("Clean the containers and kept items themselves: bins wiped inside and out before anything returns.");
    out.push("Inspect while you clean: leaks, wear, loose hardware, frayed cords. Write down anything you cannot fix today.");
    if(has(zone,"bath","shower","toilet","sink","washer","tub")) out.push("Finish by drying all wet surfaces and running ventilation 15 to 20 minutes. Dry zones do not grow mildew.");
  }
  if(i===3){
    out.push("Walk the eight hazard families in order: egress, stability, chemicals, heat, electrical, sharps, moisture, lifting.");
    if(zone.h) out.push(`This zone's known risks, ${zone.h}, verify each one is corrected or controlled, not just tidied around.`);
    if(has(zone,"chemical","cleaner","detergent","medicine","paint","solvent","finishing","under-sink")) out.push("Chemical check: original containers only, chlorine never stored beside ammonia, and everything locked or high if children ever visit.");
    if(has(zone,"kids","nursery","crib","toy","changing")) out.push("Child-height sweep: anchor tip-able furniture, secure cords out of reach, and remove any part smaller than a toilet-paper tube from floor level.");
    if(has(zone,"outlet","cord","charging","media","electronic","power tool","appliance")) out.push("Electrical: no daisy-chained strips, cords out of walk paths and pinch points, and any warm plug or frayed jacket is a stop-and-fix.");
    out.push("Correct-or-control: fix everything under two minutes now; everything else goes on a dated fix-it list before you leave the zone.");
  }
  if(i===4){
    out.push("Take your after photo from the same angle as the before. That photo is now the zone's reference standard.");
    out.push(zone.s?`Label every home, ${zone.s}, names facing out, readable from where you stand.`:"Label every home, names facing out, readable from where you stand.");
    out.push("Set quantity limits and make them visible: the basket's rim, a number on the shelf edge, a line on the bin.");
    if(has(zone,"pantry","paper","supply","detergent","diaper","backstock","linen","snack")) out.push("Write par levels for consumables: min triggers the shopping list, max stops the buying.");
    out.push(`Check the one-glance test: a tired family member should see done instantly. Done here means ${zone.g}`);
  }
  if(i===5){
    out.push("Name the owner: one person, by name, written on the standard.");
    out.push("Anchor the reset to a trigger that already happens daily: after dinner, before the school run, Sunday coffee.");
    out.push("Set the audit cadence, weekly for high-traffic zones, monthly otherwise, two minutes, compared against the reference photo.");
    out.push("Two failed audits in a row means the standard is wrong: redesign the zone, do not blame the household.");
  }
  return out;
}

/* ================= storage: localStorage (state) + IndexedDB (photos) ================= */
const LS={
  get(k,d){try{const v=localStorage.getItem("6smz:"+k);return v==null?d:JSON.parse(v);}catch(e){return d;}},
  set(k,v){try{localStorage.setItem("6smz:"+k,JSON.stringify(v));return true;}catch(e){toast("Storage full; some data may not persist.");return false;}},
  del(k){try{localStorage.removeItem("6smz:"+k);}catch(e){}},
};
let idb=null, idbReady=false;
const memPhotos={}; // fallback when IndexedDB unavailable (e.g. file://)
function openIDB(){
  return new Promise(res=>{
    try{
      const r=indexedDB.open("6smz-photos",1);
      r.onupgradeneeded=e=>{const db=e.target.result; if(!db.objectStoreNames.contains("photos")) db.createObjectStore("photos");};
      r.onsuccess=e=>{idb=e.target.result; idbReady=true; res(true);};
      r.onerror=()=>{idbReady=false; res(false);};
    }catch(e){res(false);}
  });
}
function putPhoto(id,dataUrl){
  if(!idb){memPhotos[id]=dataUrl; return Promise.resolve();}
  return new Promise((res,rej)=>{const tx=idb.transaction("photos","readwrite");tx.objectStore("photos").put(dataUrl,id);tx.oncomplete=()=>res();tx.onerror=()=>{memPhotos[id]=dataUrl;res();};});
}
function getPhoto(id){
  if(!idb) return Promise.resolve(memPhotos[id]||null);
  return new Promise(res=>{const tx=idb.transaction("photos","readonly");const rq=tx.objectStore("photos").get(id);rq.onsuccess=()=>res(rq.result||memPhotos[id]||null);rq.onerror=()=>res(memPhotos[id]||null);});
}
function delPhoto(id){delete memPhotos[id]; if(idb){try{idb.transaction("photos","readwrite").objectStore("photos").delete(id);}catch(e){}}}

/* ================= app state ================= */
let home=LS.get("home",null);
let prog=LS.get("prog",{});
let gear=new Set(LS.get("gear",[]));
let settings=LS.get("settings",{aiEndpoint:"",owner:""});
let nav={v:"dash",rid:null,zid:null};
const saveProg=()=>LS.set("prog",prog);
const saveGear=()=>LS.set("gear",[...gear]);
const pkey=(r,z)=>r+"/"+z;
const activeRooms=()=>home?ROOMS.filter(r=>home.rooms.includes(r.id)):[];
const genId=()=>Date.now().toString(36)+Math.random().toString(36).slice(2,7);
const fmtMin=m=>{const h=Math.floor(m/60);return h?`${h}h ${String(m%60).padStart(2,"0")}m`:`${m} min`;};

/* ================= image compression (canvas) ================= */
function compress(file){
  return new Promise((resolve,reject)=>{
    if(file.size>40*1024*1024){reject(new Error("Image too large (over 40 MB)."));return;}
    const rd=new FileReader();
    rd.onload=e=>{
      const im=new Image();
      im.onload=()=>{
        let dim=1100,q=0.7;
        const draw=d=>{const c=document.createElement("canvas");const sc=Math.min(1,d/Math.max(im.width,im.height));c.width=Math.max(1,Math.round(im.width*sc));c.height=Math.max(1,Math.round(im.height*sc));c.getContext("2d").drawImage(im,0,0,c.width,c.height);return c.toDataURL("image/jpeg",q);};
        let out=draw(dim);
        while(out.length>MAX_CHARS){ if(q>0.42){q-=0.1;} else if(dim>360){dim=Math.round(dim*0.72);q=0.6;} else break; out=draw(dim);}
        resolve(out);
      };
      im.onerror=()=>reject(new Error("Could not read that image."));
      im.src=e.target.result;
    };
    rd.onerror=()=>reject(new Error("Could not read that file."));
    rd.readAsDataURL(file);
  });
}

/* ================= AI (configurable endpoint) ================= */
function extractJson(text){
  const cleaned=text.replace(/```json|```/g,"").trim();
  const s=cleaned.indexOf("{"); if(s<0) throw new Error("the AI reply contained no JSON");
  let depth=0,inStr=false,esc=false,end=-1;
  for(let i=s;i<cleaned.length;i++){const ch=cleaned[i];
    if(inStr){if(esc)esc=false;else if(ch==="\\")esc=true;else if(ch==='"')inStr=false;}
    else if(ch==='"')inStr=true; else if(ch==="{")depth++; else if(ch==="}"){depth--;if(!depth){end=i;break;}}}
  const frag=end>=0?cleaned.slice(s,end+1):cleaned.slice(s);
  if(end>=0) return JSON.parse(frag); return repairParse(frag);
}
function balanceClose(s){let d=0,a=0,str=false,esc=false;for(const ch of s){if(str){if(esc)esc=false;else if(ch==="\\")esc=true;else if(ch==='"')str=false;}else if(ch==='"')str=true;else if(ch==="{")d++;else if(ch==="}")d--;else if(ch==="[")a++;else if(ch==="]")a--;}if(str)s+='"';s=s.replace(/,\s*$/,"");return s+"]".repeat(Math.max(0,a))+"}".repeat(Math.max(0,d));}
function repairParse(frag){const pts=[frag.length];for(let i=frag.length-1;i>0&&pts.length<300;i--){const ch=frag[i];if(ch===",")pts.push(i);else if(ch==="}"||ch==="]"||ch==='"')pts.push(i+1);}for(const cut of pts){try{return JSON.parse(balanceClose(frag.slice(0,cut)));}catch(e){}}throw new Error("the AI reply was cut off and could not be repaired");}
async function aiShrink(url){
  if(url.length<140000) return url;
  return await new Promise(res=>{const im=new Image();im.onload=()=>{const c=document.createElement("canvas");const sc=Math.min(1,640/Math.max(im.width,im.height));c.width=Math.round(im.width*sc);c.height=Math.round(im.height*sc);c.getContext("2d").drawImage(im,0,0,c.width,c.height);res(c.toDataURL("image/jpeg",0.55));};im.onerror=()=>res(url);im.src=url;});
}
async function callAI(prompt,urls){
  const ep=(settings.aiEndpoint||"").trim();
  if(!ep) throw new Error("NO_ENDPOINT");
  const imgs=[];
  for(const u of urls){const s=await aiShrink(u);imgs.push({type:"image",source:{type:"base64",media_type:"image/jpeg",data:s.split(",")[1]}});}
  const content=[...imgs,{type:"text",text:prompt}];
  const ctrl=new AbortController();const timer=setTimeout(()=>ctrl.abort(),60000);
  try{
    const r=await fetch(ep,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:"claude-sonnet-4-6",max_tokens:1200,messages:[{role:"user",content}]}),signal:ctrl.signal});
    const data=await r.json();
    if(data.error) throw new Error(data.error.message||"AI request failed");
    const text=(data.content||[]).filter(b=>b.type==="text").map(b=>b.text).join("\n");
    if(!text.trim()) throw new Error("the AI sent an empty reply");
    return extractJson(text);
  } finally{ clearTimeout(timer); }
}
const beforePrompt=z=>`You are a world-class professional home organizer and Lean Six Sigma practitioner reviewing BEFORE photos of one micro zone in a client's home.
ZONE: ${z.n}
PRIMARY FUNCTION: ${z.f}
ITEMS THAT TYPICALLY BELONG HERE: ${z.i}
TARGET COMPLETED STATE: ${z.g}
KNOWN HAZARD PATTERNS: ${z.h||"general household hazards"}
Look carefully at the photo(s). Respond with ONLY minified JSON, no preamble, no markdown fences, exactly this shape:
{"belongs":["visible items that serve this zone's function"],"review":[{"item":"visible item that likely does NOT belong","verdict":"relocate"|"donate"|"discard"|"keep-maybe","why":"one short reason"}],"hazards":["only hazards actually visible"],"plan":"2-3 sentences of specific Sort guidance for THIS zone","clutter_score":1-5}
Rules: clutter_score 1 = near target, 5 = heavily cluttered. Only list things visibly present. Max 6 belongs, 8 review, 3 hazards. Every why under 8 words, plan under 45 words.`;
const afterPrompt=(z,hasB)=>`You are a world-class professional home organizer coaching a client who just finished a 6S reset of one micro zone. ${hasB?"The FIRST image(s) are BEFORE, the LAST are AFTER.":"The image(s) show the AFTER state."}
ZONE: ${z.n}
PRIMARY FUNCTION: ${z.f}
TARGET COMPLETED STATE: ${z.g}
Respond with ONLY minified JSON, exactly this shape:
{"score":1-5,"meets_standard":true|false,"wins":["specific visible improvements, max 4"],"remaining":["specific gaps vs target, max 3, empty if none"],"coach":"2-3 warm specific sentences"}
Rules: score 5 = fully matches target. Max 3 wins, 2 remaining, coach under 40 words. Honest and kind, a celebration with a professional eye.`;

/* ================= tiny DOM helpers ================= */
const $=(s,r=document)=>r.querySelector(s);
const el=(tag,attrs={},...kids)=>{const e=document.createElement(tag);for(const k in attrs){if(k==="class")e.className=attrs[k];else if(k==="html")e.innerHTML=attrs[k];else if(k.startsWith("on"))e.addEventListener(k.slice(2),attrs[k]);else if(k==="style")e.setAttribute("style",attrs[k]);else e.setAttribute(k,attrs[k]);}for(const kid of kids){if(kid==null)continue;e.append(kid.nodeType?kid:document.createTextNode(kid));}return e;};
function toast(msg){let t=$("#toast");if(!t){t=el("div",{id:"toast"});document.body.append(t);}t.textContent=msg;t.classList.add("show");clearTimeout(toast._t);toast._t=setTimeout(()=>t.classList.remove("show"),3400);}
const esc=s=>(s==null?"":String(s)).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

/* ================= progress helpers ================= */
function zoneProg(r,z){const k=pkey(r,z);if(!prog[k])prog[k]={steps:[false,false,false,false,false,false],sb:[0,0,0,0,0,0],bp:[],ap:[],out:{r:0,d:0,t:0},done:false,ai:null,aiA:null,audit:null,drift:false};return prog[k];}
function zoneStats(){let zr=0,mins=0,items=0;for(const r of activeRooms())for(const z of r.z){const p=prog[pkey(r.id,z.id)];if(p){if(p.done)zr++;mins+=(p.steps.filter(Boolean).length/6)*z.t.reduce((a,b)=>a+b,0);if(p.out)items+=(p.out.d||0)+(p.out.t||0)+(p.out.r||0);}}return{zr,mins:Math.round(mins),items};}

/* ================= navigation ================= */
function go(v,rid,zid){nav={v,rid:rid??nav.rid,zid:zid??nav.zid};window.scrollTo(0,0);render();}

/* ================= render root ================= */
function render(){
  const root=$("#root");root.innerHTML="";
  if(!home){root.append(Setup());return;}
  if(nav.v==="dash")root.append(Dashboard());
  else if(nav.v==="room")root.append(RoomScreen());
  else if(nav.v==="zone")root.append(ZoneScreen());
  else if(nav.v==="settings")root.append(Settings());
}

/* ---------- Setup ---------- */
function Setup(){
  const wrap=el("div",{class:"screen"});
  const chosen=new Set(ROOMS.map(r=>r.id)); // curated set: all preselected
  let name="";
  const rerender=()=>{
    const zc=ROOMS.filter(r=>chosen.has(r.id)).reduce((a,r)=>a+r.z.length,0);
    stat.textContent=`${chosen.size} rooms · ${zc} zones`;
    start.disabled=chosen.size===0;
  };
  const grid=el("div",{class:"roomgrid"});
  ROOMS.forEach(r=>{
    const b=el("button",{class:"roomchip on",onclick:()=>{if(chosen.has(r.id))chosen.delete(r.id);else chosen.add(r.id);b.classList.toggle("on");rerender();}}, r.n);
    grid.append(b);
  });
  const stat=el("div",{class:"muted",style:"margin:10px 0"});
  const start=el("button",{class:"btn primary block",onclick:()=>{home={name:name||"Our Home",rooms:ROOMS.filter(r=>chosen.has(r.id)).map(r=>r.id)};LS.set("home",home);go("dash");}},"Start my reset");
  wrap.append(
    el("div",{class:"hero"},
      el("p",{class:"eyebrow"},"6S Success · Home Micro Zones"),
      el("h1",{},"Organization & Housekeeping"),
      el("p",{class:"lede"},"Reset your home one micro zone at a time. Pick a zone, photograph the truth, work the six steps, and see the change from the doorway.")),
    el("label",{class:"fieldlbl"},"Household name (optional)"),
    el("input",{class:"txt",placeholder:"The Harper House",oninput:e=>name=e.target.value}),
    el("p",{class:"fieldlbl",style:"margin-top:18px"},"Rooms in this beta"),
    grid,stat,start,
    el("p",{class:"fineprint"},"MVP Beta. Photos and progress stay on this device. AI coaching is optional and off until you add an endpoint in Settings.")
  );
  rerender();
  return wrap;
}

/* ---------- Dashboard ---------- */
function Dashboard(){
  const wrap=el("div",{class:"screen"});
  const s=zoneStats();
  wrap.append(TopBar(home.name,null,el("button",{class:"icon",onclick:()=>go("settings")},"⚙")));
  wrap.append(el("div",{class:"stats"},
    stat(s.zr,"zones reset"),stat(fmtMin(s.mins),"time invested"),stat(s.items,"items released")));
  // next up
  let next=null;
  for(const r of activeRooms()){for(const z of r.z){const p=prog[pkey(r.id,z.id)];if(p&&!p.done&&p.steps.some(Boolean)){next={r,z,label:"Pick up where you left off"};break;}}if(next)break;}
  if(!next)for(const r of activeRooms()){for(const z of r.z){const p=prog[pkey(r.id,z.id)];if(!p||!p.done){next={r,z,label:"Next up"};break;}}if(next)break;}
  if(next)wrap.append(el("button",{class:"nextcard",onclick:()=>go("zone",next.r.id,next.z.id)},
    el("span",{class:"eyebrow"},next.label),el("strong",{},next.z.n),el("span",{class:"muted"},next.r.n+" · "+fmtMin(next.z.t.reduce((a,b)=>a+b,0)))));
  // audit due
  const dueList=[];const now=Date.now();
  for(const r of activeRooms())for(const z of r.z){const p=prog[pkey(r.id,z.id)];if(p&&p.done&&(p.drift||(p.audit&&now-p.audit>7*864e5)))dueList.push({r,z});}
  if(dueList.length)wrap.append(el("div",{class:"banner"},`${dueList.length} zone${dueList.length>1?"s":""} due for a check-in`));
  // room cards
  activeRooms().forEach(r=>{
    const total=r.z.length;const done=r.z.filter(z=>{const p=prog[pkey(r.id,z.id)];return p&&p.done;}).length;
    const pct=Math.round(done/total*100);
    const dots=el("div",{class:"dots"});r.z.forEach(z=>{const p=prog[pkey(r.id,z.id)];const cls=p&&p.done?"done":(p&&p.steps.some(Boolean)?"part":"");dots.append(el("span",{class:"dot "+cls}));});
    wrap.append(el("button",{class:"roomcard",onclick:()=>go("room",r.id)},
      el("div",{class:"rc-ring",style:`--pct:${pct}`},el("span",{},pct+"%")),
      el("div",{class:"rc-body"},el("strong",{},r.n),el("span",{class:"muted"},`${done}/${total} zones · ${fmtMin(r.z.reduce((a,z)=>a+z.t.reduce((x,y)=>x+y,0),0))}`),dots)));
  });
  return wrap;
}
function stat(v,l){return el("div",{class:"statcard"},el("div",{class:"statnum"},String(v)),el("div",{class:"statlbl"},l));}

/* ---------- Room ---------- */
function RoomScreen(){
  const r=ROOMS.find(x=>x.id===nav.rid);
  const wrap=el("div",{class:"screen"});
  wrap.append(TopBar(r.n,()=>go("dash")));
  r.z.forEach((z,i)=>{
    const p=prog[pkey(r.id,z.id)];
    const doneN=p?p.steps.filter(Boolean).length:0;
    const spine=el("div",{class:"spine"});
    z.t.forEach((t,si)=>spine.append(el("span",{class:"seg",style:`flex:${t};background:${p&&p.steps[si]?STEP_C[si]:"#e4dcce"}`})));
    const pills=el("div",{class:"pillrow"});
    if(p&&p.done)pills.append(el("span",{class:"pill done"},"Done"));
    else if(doneN)pills.append(el("span",{class:"pill part"},doneN+"/6"));
    if(p&&(p.bp.length||p.ap.length))pills.append(el("span",{class:"pill"},`${p.bp.length+p.ap.length} photo${p.bp.length+p.ap.length>1?"s":""}`));
    if(p&&p.ai)pills.append(el("span",{class:"pill ai"},"AI plan"));
    wrap.append(el("button",{class:"zonecard",onclick:()=>go("zone",r.id,z.id)},
      el("div",{class:"zc-top"},el("strong",{},z.n),el("span",{class:"muted mono"},fmtMin(z.t.reduce((a,b)=>a+b,0)))),
      el("div",{class:"muted sm"},z.f),spine,pills));
  });
  return wrap;
}

/* ---------- Zone runner ---------- */
function ZoneScreen(){
  const r=ROOMS.find(x=>x.id===nav.rid), z=r.z.find(x=>x.id===nav.zid);
  const p=zoneProg(r.id,z.id);
  const wrap=el("div",{class:"screen"});
  wrap.append(TopBar(z.n,()=>go("room",r.id)));
  // mission
  wrap.append(el("div",{class:"card mission"},
    el("p",{class:"eyebrow"},"The mission"),
    el("p",{},el("b",{},"Function. "),z.f),
    el("p",{},el("b",{},"Done looks like. "),z.g),
    z.h?el("p",{class:"hazard"},el("b",{},"Watch for. "),z.h):null,
    z.c?el("p",{class:"cue"},el("b",{},"Expert cue. "),z.c):null));

  // before photos + AI sort plan
  wrap.append(PhotoBlock("before",r,z,p));
  wrap.append(SortPlanBlock(r,z,p));

  // steps
  const stepsWrap=el("div",{class:"steps"});
  STEPS.forEach((st,i)=>stepsWrap.append(StepPanel(r,z,p,st,i)));
  wrap.append(stepsWrap);

  // after photos + coach
  wrap.append(PhotoBlock("after",r,z,p));
  wrap.append(CoachBlock(r,z,p));

  // sustain audit (after done)
  if(p.done)wrap.append(AuditBlock(r,z,p));
  return wrap;
}

function PhotoBlock(which,r,z,p){
  const arr=which==="before"?p.bp:p.ap;
  const box=el("div",{class:"card"});
  box.append(el("p",{class:"eyebrow"},which==="before"?"Before · the honest truth":"After · the win"));
  const grid=el("div",{class:"photogrid"});
  const paint=async()=>{
    grid.innerHTML="";
    for(const id of arr){const url=await getPhoto(id);const im=el("div",{class:"thumb",style:`background-image:url(${url})`,onclick:()=>lightbox(url,()=>{delPhoto(id);arr.splice(arr.indexOf(id),1);saveProg();paint();})});grid.append(im);}
    if(arr.length<MAX_PHOTOS){
      const inp=el("input",{type:"file",accept:"image/*",capture:"environment",multiple:"",style:"display:none",onchange:async e=>{
        const files=[...e.target.files].slice(0,MAX_PHOTOS-arr.length);
        for(const f of files){try{const durl=await compress(f);const id=genId();await putPhoto(id,durl);arr.push(id);}catch(err){toast(err.message);}}
        // auto-complete: after photo + all steps => done
        if(which==="after"&&p.steps.every(Boolean)&&arr.length&&!p.done){p.done=true;p.audit=Date.now();}
        saveProg();paint();refreshCoach&&refreshCoach();
      }});
      const add=el("button",{class:"addphoto",onclick:()=>inp.click()},"＋ Add photo");
      grid.append(add,inp);
    }
  };
  paint();box.append(grid,el("p",{class:"fineprint"},"Stays on this device. Sent to AI only when you tap the AI button."));
  return box;
}

let refreshCoach=null;
function SortPlanBlock(r,z,p){
  const box=el("div",{class:"card"});
  box.append(el("p",{class:"eyebrow"},"AI Sort plan"));
  const body=el("div",{});
  const render=()=>{
    body.innerHTML="";
    if(p.ai){
      const a=p.ai;
      body.append(el("div",{class:"scorepill"},`Clutter ${a.clutter_score||"?"}/5`));
      if(a.plan)body.append(el("p",{},a.plan));
      if(a.review&&a.review.length){body.append(el("p",{class:"eyebrow sm"},"Decide on these"));
        a.review.forEach(it=>{const v=VERDICT[it.verdict]||{c:"#675f57",label:it.verdict};
          body.append(el("div",{class:"reviewrow"},el("span",{class:"vchip",style:`background:${v.c}`},v.label),el("span",{},esc(it.item)+(it.why?" · "+esc(it.why):""))));});}
      if(a.hazards&&a.hazards.length){body.append(el("div",{class:"hazbox"},el("b",{},"Visible hazards. "),a.hazards.join("; ")));}
    }else{
      body.append(el("p",{class:"muted"},"Tap below to get an AI Sort plan from your before photos, or just start with Sort using the built-in guidance."));
    }
  };
  const btn=el("button",{class:"btn block",onclick:async()=>{
    if(!p.bp.length){toast("Add a before photo first.");return;}
    btn.disabled=true;btn.textContent="Reading your photos…";
    try{const urls=[];for(const id of p.bp.slice(0,2)){urls.push(await getPhoto(id));}
      p.ai=await callAI(beforePrompt(z),urls);saveProg();render();
    }catch(err){toast(err.message==="NO_ENDPOINT"?"Add an AI endpoint in Settings to enable AI plans.":("AI: "+err.message));}
    btn.disabled=false;btn.textContent=p.ai?"Rebuild plan":"Build my Sort plan";
  }},p.ai?"Rebuild plan":"Build my Sort plan");
  render();box.append(body,btn);
  return box;
}

function StepPanel(r,z,p,st,i){
  const open={v:false};
  const panel=el("div",{class:"steppanel"});
  const head=el("button",{class:"stephead",onclick:()=>{open.v=!open.v;bodyWrap.style.display=open.v?"block":"none";chev.textContent=open.v?"▾":"▸";}},
    el("span",{class:"stepnum",style:`background:${STEP_C[i]}`},String(i+1)),
    el("span",{class:"stepk"},st.k,el("span",{class:"steptag"},st.tag)),
    el("span",{class:"chev"},"▸"));
  const chev=head.querySelector(".chev");
  const bodyWrap=el("div",{class:"stepbody",style:"display:none"});
  bodyWrap.append(el("p",{class:"stepmeta"},st.meta));
  // inputs
  const inputs=stepInputs(z,i,gear);
  if(inputs.length){
    const chips=el("div",{class:"chips"});
    inputs.forEach(inp=>chips.append(el("button",{class:"chip"+(inp.own?" own":""),onclick:()=>productSheet(inp)},(inp.own?"✓ ":"")+inp.n)));
    bodyWrap.append(el("p",{class:"eyebrow sm"},"You'll need · tap to source"),chips);
  }else{
    bodyWrap.append(el("p",{class:"eyebrow sm"},"You'll need"),el("p",{class:"muted sm"},st.needs(z)));
  }
  // substeps
  const subs=subSteps(z,i);
  const sl=el("div",{class:"substeps"});
  subs.forEach((txt,j)=>{
    const on=(p.sb[i]>>j)&1;
    const row=el("button",{class:"substep"+(on?" on":""),onclick:()=>{p.sb[i]^=(1<<j);saveProg();row.classList.toggle("on");}},el("span",{class:"cbox"},on?"✓":""),el("span",{},txt));
    sl.append(row);
  });
  bodyWrap.append(el("p",{class:"eyebrow sm"},"How to do it"),sl);
  // sort tally
  if(i===0){
    const t=el("div",{class:"tallies"});
    [["r","Relocated"],["d","Donated"],["t","Discarded"]].forEach(([k,lbl])=>{
      const val=el("span",{class:"tval"},String(p.out[k]||0));
      t.append(el("div",{class:"tally"},el("span",{},lbl),el("div",{class:"tbtns"},
        el("button",{onclick:()=>{p.out[k]=Math.max(0,(p.out[k]||0)-1);val.textContent=p.out[k];saveProg();}},"−"),val,
        el("button",{onclick:()=>{p.out[k]=(p.out[k]||0)+1;val.textContent=p.out[k];saveProg();}},"＋"))));
    });
    bodyWrap.append(el("p",{class:"eyebrow sm"},"Out the door"),t);
  }
  bodyWrap.append(el("p",{class:"donewhen"},el("b",{},"Done when. "),st.done(z)));
  // done toggle
  const dbtn=el("button",{class:"btn block "+(p.steps[i]?"okdone":""),onclick:()=>{
    p.steps[i]=!p.steps[i];
    p.done=p.steps.every(Boolean)&&p.ap.length>0;
    if(p.done&&!p.audit)p.audit=Date.now();
    saveProg();render();
  }},p.steps[i]?"✓ Done":"Mark "+st.k+" done");
  bodyWrap.append(dbtn);
  panel.append(head,bodyWrap);
  if(p.steps[i])head.classList.add("stepdone");
  return panel;
}

function CoachBlock(r,z,p){
  const box=el("div",{class:"card"});
  box.append(el("p",{class:"eyebrow"},"Coach's review"));
  const body=el("div",{});
  const render=()=>{
    body.innerHTML="";
    if(p.aiA){const a=p.aiA;
      body.append(el("div",{class:"scorepill "+(a.meets_standard?"good":"")},`${a.score}/5 ${a.meets_standard?"· meets standard":""}`));
      if(a.coach)body.append(el("p",{},a.coach));
      if(a.wins&&a.wins.length){body.append(el("p",{class:"eyebrow sm"},"Wins"));a.wins.forEach(w=>body.append(el("div",{class:"winrow"},"✓ "+esc(w))));}
      if(a.remaining&&a.remaining.length){body.append(el("p",{class:"eyebrow sm"},"Still to do"));a.remaining.forEach(w=>body.append(el("div",{class:"remrow"},"• "+esc(w))));}
    }else body.append(el("p",{class:"muted"},"Finish the six steps, add an after photo, then get a scored review."));
  };
  const btn=el("button",{class:"btn block",onclick:async()=>{
    if(!p.ap.length){toast("Add an after photo first.");return;}
    btn.disabled=true;btn.textContent="Reviewing…";
    try{const urls=[];for(const id of p.bp.slice(0,1))urls.push(await getPhoto(id));for(const id of p.ap.slice(0,2))urls.push(await getPhoto(id));
      p.aiA=await callAI(afterPrompt(z,p.bp.length>0),urls);saveProg();render();
    }catch(err){toast(err.message==="NO_ENDPOINT"?"Add an AI endpoint in Settings to enable AI reviews.":("AI: "+err.message));}
    btn.disabled=false;btn.textContent=p.aiA?"Review again":"Get my review";
  }},p.aiA?"Review again":"Get my review");
  render();box.append(body,btn);
  refreshCoach=render;
  return box;
}

function AuditBlock(r,z,p){
  const box=el("div",{class:"card audit"});
  box.append(el("p",{class:"eyebrow"},"Sustain · keep it"),
    el("p",{class:"muted"},"A two-minute check against your after photo. Owner and trigger keep it alive."));
  box.append(el("div",{class:"auditbtns"},
    el("button",{class:"btn ghost",onclick:()=>{p.audit=Date.now();p.drift=false;saveProg();toast("Logged: holding.");render();}},"Holding"),
    el("button",{class:"btn ghost warn",onclick:()=>{p.audit=Date.now();p.drift=true;saveProg();toast("Logged: drift noted.");render();}},"Drift noted")));
  box.append(el("button",{class:"btn ghost block",style:"margin-top:8px",onclick:()=>{p.steps=[false,false,false,false,false,false];p.done=false;saveProg();render();}},"Run this zone again"));
  return box;
}

/* ---------- product sheet + lightbox ---------- */
function productSheet(inp){
  const p=PRODUCTS[inp.i];
  const back=el("div",{class:"sheetback",onclick:e=>{if(e.target===back)close();}});
  const close=()=>back.remove();
  const owned=gear.has(inp.i);
  const sheet=el("div",{class:"sheet"},
    el("div",{class:"sheethandle"}),
    el("p",{class:"eyebrow"},LEVELS[inp.lvl]||""),
    el("h3",{},p.n),
    el("p",{},p.o||inp.use||""),
    el("p",{class:"muted sm"},`Use here: ${inp.use||"general"} · about $${midCost(p)}`),
    p.s?el("p",{class:"hazbox sm"},el("b",{},"Safety. "),p.s):null,
    el("button",{class:"btn block "+(owned?"okdone":""),onclick:()=>{if(gear.has(inp.i))gear.delete(inp.i);else gear.add(inp.i);saveGear();close();render();}},owned?"✓ I own this":"Mark as owned"));
  // three picks (names only for beta; no dated prices/links)
  const picks=el("div",{class:"picks"});
  PICKS.forEach(([k,lbl])=>{const pk=p[k];if(pk&&pk.t)picks.append(el("div",{class:"pickcard"},el("span",{class:"eyebrow sm"},lbl),el("strong",{},pk.t)));});
  if(picks.children.length){sheet.append(el("p",{class:"eyebrow sm",style:"margin-top:14px"},"Three ways to buy"),picks,el("p",{class:"fineprint"},"Names shown for the beta. Confirm current price and availability at your retailer."));}
  sheet.append(el("button",{class:"btn ghost block",style:"margin-top:12px",onclick:close},"Close"));
  back.append(sheet);document.body.append(back);
}
function lightbox(url,onDelete){
  const back=el("div",{class:"lightback",onclick:e=>{if(e.target===back)back.remove();}});
  back.append(el("img",{src:url,class:"lightimg"}),
    el("div",{class:"lightbtns"},
      el("button",{class:"btn ghost",onclick:()=>back.remove()},"Close"),
      el("button",{class:"btn ghost warn",onclick:()=>{if(confirm("Delete this photo?")){onDelete();back.remove();}}},"Delete")));
  document.body.append(back);
}

/* ---------- Settings ---------- */
function Settings(){
  const wrap=el("div",{class:"screen"});
  wrap.append(TopBar("Settings",()=>go("dash")));
  wrap.append(el("div",{class:"card"},
    el("p",{class:"eyebrow"},"AI coaching (optional)"),
    el("p",{class:"muted sm"},"AI Sort plans and reviews are OFF until you add an endpoint. For the beta this is a server proxy URL that holds the API key. No key is ever stored in this app. Leave blank to use the built-in static guidance."),
    el("label",{class:"fieldlbl"},"AI endpoint URL"),
    el("input",{class:"txt",value:settings.aiEndpoint||"",placeholder:"https://your-proxy.example.com/ai",oninput:e=>{settings.aiEndpoint=e.target.value.trim();LS.set("settings",settings);}}),
    el("p",{class:"fineprint"},"The app POSTs an Anthropic-style messages body to this URL and expects the messages response back. Your proxy adds the key and enforces zero-retention.")));
  wrap.append(el("div",{class:"card"},
    el("p",{class:"eyebrow"},"Household"),
    el("label",{class:"fieldlbl"},"Name"),
    el("input",{class:"txt",value:home.name,oninput:e=>{home.name=e.target.value;LS.set("home",home);}})));
  wrap.append(el("div",{class:"card"},
    el("p",{class:"eyebrow"},"Data"),
    el("p",{class:"muted sm"},"Everything is on this device. Wipe removes all progress and photos."),
    el("button",{class:"btn ghost warn block",onclick:async()=>{if(confirm("Erase all progress and photos on this device?")){for(const k in prog){const p=prog[k];[...(p.bp||[]),...(p.ap||[])].forEach(delPhoto);}prog={};gear=new Set();LS.del("prog");LS.del("gear");saveProg();saveGear();toast("Erased.");go("dash");}}},"Erase everything")));
  wrap.append(el("p",{class:"fineprint",style:"text-align:center;margin-top:20px"},"6S Success Home Micro Zones · MVP Beta · v0.1"));
  return wrap;
}

/* ---------- shared bits ---------- */
function TopBar(title,onBack,right){
  return el("div",{class:"topbar"},
    onBack?el("button",{class:"icon",onclick:onBack},"‹"):el("span",{class:"icon"},""),
    el("h2",{class:"topttl"},title),
    right||el("span",{class:"icon"},""));
}

/* ================= boot ================= */
(async function(){await openIDB();render();
  if(!idbReady)toast("Running with in-memory photos (open over http for persistent photos).");
})();
"""

CSS = r"""
:root{--paper:#f4efe6;--panel:#fffdf8;--ink:#241f1a;--soft:#675f57;--navy:#16395f;
--green:#3f6647;--amber:#b8862b;--red:#a8452f;--plum:#6b4f8a;--teal:#3d6d74;--rule:#dcd0be;
--serif:'Iowan Old Style','Palatino Linotype',Georgia,serif;--sans:'Avenir Next','Segoe UI',system-ui,Arial,sans-serif;
--mono:'SF Mono',Consolas,Menlo,monospace;}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.5;font-size:16px}
#root{max-width:560px;margin:0 auto;min-height:100vh}
.screen{padding:0 16px 110px}
h1,h2,h3{font-family:var(--serif);color:var(--navy);margin:0}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--amber);font-weight:700;margin:0 0 6px}
.eyebrow.sm{font-size:10px;margin:12px 0 5px;color:var(--soft)}
.muted{color:var(--soft)}.sm{font-size:13.5px}.mono{font-family:var(--mono)}
.fineprint{color:var(--soft);font-size:12px;margin-top:12px;line-height:1.45}
.hero{padding:44px 0 10px}.hero h1{font-size:32px;line-height:1.08;margin:6px 0}.lede{color:var(--soft);margin-top:10px}
.fieldlbl{font-size:12.5px;font-weight:700;color:var(--soft);display:block;margin-bottom:5px}
.txt{width:100%;padding:12px 14px;border:1.5px solid var(--rule);border-radius:10px;background:var(--panel);font-size:16px;font-family:inherit;color:var(--ink)}
.roomgrid{display:flex;flex-wrap:wrap;gap:8px}
.roomchip{border:1.5px solid var(--rule);background:var(--panel);color:var(--soft);border-radius:20px;padding:9px 14px;font-size:14px;font-weight:600;font-family:inherit}
.roomchip.on{border-color:var(--green);background:#eef2ea;color:var(--green)}
.btn{border:none;border-radius:10px;padding:13px 18px;font-size:15.5px;font-weight:600;font-family:inherit;background:var(--panel);color:var(--navy);border:1.5px solid var(--rule)}
.btn.primary{background:var(--green);color:#fffdf8;border-color:var(--green)}
.btn.block{display:block;width:100%;margin-top:12px}
.btn.ghost{background:transparent}
.btn.ghost.warn{border-color:var(--red);color:var(--red)}
.btn.okdone{background:#eef2ea;color:var(--green);border-color:var(--green)}
.btn:disabled{opacity:.55}
.topbar{position:sticky;top:0;background:rgba(244,239,230,.94);backdrop-filter:blur(8px);display:flex;align-items:center;gap:8px;padding:14px 0 10px;z-index:20;border-bottom:1px solid var(--rule);margin-bottom:14px}
.topttl{flex:1;font-size:21px;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.icon{width:40px;height:40px;border:none;background:transparent;font-size:24px;color:var(--navy);border-radius:10px}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:16px}
.statcard{background:var(--panel);border:1px solid var(--rule);border-radius:12px;padding:14px 10px;text-align:center}
.statnum{font-family:var(--serif);font-size:22px;font-weight:700;color:var(--green)}
.statlbl{font-size:11px;color:var(--soft);margin-top:2px}
.nextcard{display:flex;flex-direction:column;gap:3px;width:100%;text-align:left;background:var(--navy);color:#fffdf8;border:none;border-radius:14px;padding:18px;margin-bottom:16px}
.nextcard .eyebrow{color:#e9c877}.nextcard strong{font-family:var(--serif);font-size:20px}.nextcard .muted{color:#cdd7df}
.banner{background:#f6f1e3;border:1px solid var(--amber);color:#7a5b16;border-radius:10px;padding:11px 15px;font-size:14px;margin-bottom:14px}
.roomcard{display:flex;align-items:center;gap:14px;width:100%;text-align:left;background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:15px;margin-bottom:11px}
.rc-ring{width:52px;height:52px;border-radius:50%;flex:none;display:grid;place-items:center;font-size:12px;font-weight:700;color:var(--green);background:conic-gradient(var(--green) calc(var(--pct)*1%),#e4dcce 0)}
.rc-ring span{background:var(--panel);width:40px;height:40px;border-radius:50%;display:grid;place-items:center}
.rc-body{flex:1;display:flex;flex-direction:column;gap:3px}.rc-body strong{font-family:var(--serif);font-size:18px;color:var(--navy)}
.dots{display:flex;gap:4px;margin-top:5px;flex-wrap:wrap}.dot{width:9px;height:9px;border-radius:3px;background:#e4dcce}.dot.part{background:var(--amber)}.dot.done{background:var(--green)}
.zonecard{display:block;width:100%;text-align:left;background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:15px;margin-bottom:11px}
.zc-top{display:flex;justify-content:space-between;align-items:baseline;gap:10px}.zc-top strong{font-family:var(--serif);font-size:17px;color:var(--navy)}
.spine{display:flex;gap:2px;margin:10px 0 8px;height:8px;border-radius:5px;overflow:hidden}.seg{border-radius:2px}
.pillrow{display:flex;gap:6px;flex-wrap:wrap}
.pill{font-size:11px;font-weight:700;background:#efe9db;color:var(--soft);padding:3px 9px;border-radius:11px}
.pill.done{background:#eef2ea;color:var(--green)}.pill.part{background:#f6f1e3;color:var(--amber)}.pill.ai{background:#eaeef2;color:var(--navy)}
.card{background:var(--panel);border:1px solid var(--rule);border-radius:14px;padding:16px 17px;margin-bottom:13px}
.card.mission p{margin:6px 0}.hazard{color:#8a3a28}.cue{color:var(--teal)}
.photogrid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.thumb{aspect-ratio:1;border-radius:10px;background-size:cover;background-position:center;border:1px solid var(--rule)}
.addphoto{aspect-ratio:1;border:1.5px dashed var(--rule);background:transparent;border-radius:10px;color:var(--soft);font-size:13px;font-weight:600;font-family:inherit}
.scorepill{display:inline-block;background:#f6f1e3;color:var(--amber);font-weight:700;border-radius:11px;padding:4px 12px;font-size:13px;margin-bottom:8px}
.scorepill.good{background:#eef2ea;color:var(--green)}
.reviewrow,.winrow,.remrow{display:flex;gap:8px;align-items:center;font-size:14px;margin:5px 0}
.vchip{color:#fffdf8;font-size:10px;font-weight:700;padding:2px 8px;border-radius:9px;white-space:nowrap}
.hazbox{background:#f7ede9;border-left:3px solid var(--red);border-radius:0 8px 8px 0;padding:8px 12px;margin-top:8px;font-size:13.5px}
.steppanel{background:var(--panel);border:1px solid var(--rule);border-radius:12px;margin-bottom:9px;overflow:hidden}
.stephead{display:flex;align-items:center;gap:11px;width:100%;text-align:left;background:transparent;border:none;padding:14px 15px;font-family:inherit}
.stephead.stepdone{background:#f4f7f2}
.stepnum{width:26px;height:26px;border-radius:7px;color:#fffdf8;font-weight:700;display:grid;place-items:center;font-size:14px;flex:none}
.stepk{flex:1;font-family:var(--serif);font-size:17px;color:var(--navy);display:flex;flex-direction:column}
.steptag{font-family:var(--sans);font-size:11.5px;color:var(--soft);font-weight:400;margin-top:1px}
.chev{color:var(--soft)}
.stepbody{padding:0 15px 15px}
.stepmeta{font-size:14px;color:var(--ink);margin:0 0 8px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1.5px solid var(--rule);background:var(--panel);border-radius:9px;padding:8px 11px;font-size:13px;font-weight:600;color:var(--navy);font-family:inherit}
.chip.own{background:#eef2ea;color:var(--green);border-color:var(--green)}
.substeps{display:flex;flex-direction:column;gap:6px}
.substep{display:flex;gap:10px;align-items:flex-start;text-align:left;background:transparent;border:1px solid var(--rule);border-radius:9px;padding:10px 12px;font-size:13.5px;font-family:inherit;color:var(--ink)}
.substep.on{background:#f4f7f2;border-color:var(--green)}
.cbox{width:19px;height:19px;border:2px solid var(--rule);border-radius:5px;flex:none;display:grid;place-items:center;color:var(--green);font-size:13px;font-weight:700}
.substep.on .cbox{border-color:var(--green);background:#eef2ea}
.tallies{display:flex;flex-direction:column;gap:8px}
.tally{display:flex;justify-content:space-between;align-items:center;font-size:14px}
.tbtns{display:flex;align-items:center;gap:12px}.tbtns button{width:34px;height:34px;border:1.5px solid var(--rule);background:var(--panel);border-radius:9px;font-size:18px;color:var(--navy)}
.tval{min-width:22px;text-align:center;font-weight:700;font-family:var(--mono)}
.donewhen{font-size:13.5px;color:var(--soft);margin:12px 0 4px;background:#f7f3ea;border-radius:8px;padding:9px 12px}
.audit .auditbtns{display:flex;gap:10px}.audit .auditbtns .btn{flex:1}
.sheetback,.lightback{position:fixed;inset:0;background:rgba(20,16,12,.55);z-index:50;display:flex;align-items:flex-end}
.lightback{align-items:center;justify-content:center;flex-direction:column;gap:14px;padding:20px}
.sheet{background:var(--paper);width:100%;max-width:560px;margin:0 auto;border-radius:18px 18px 0 0;padding:10px 18px 26px;max-height:88vh;overflow:auto}
.sheethandle{width:40px;height:4px;background:var(--rule);border-radius:3px;margin:6px auto 12px}
.sheet h3{font-size:20px;margin-bottom:6px}
.picks{display:flex;flex-direction:column;gap:8px}
.pickcard{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:10px 13px;display:flex;flex-direction:column;gap:2px}
.pickcard strong{font-size:14px;color:var(--navy)}
.lightimg{max-width:100%;max-height:78vh;border-radius:12px}.lightbtns{display:flex;gap:12px}
#toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%) translateY(20px);background:var(--ink);color:var(--paper);padding:12px 18px;border-radius:11px;font-size:14px;max-width:90%;text-align:center;opacity:0;transition:.25s;z-index:80;pointer-events:none}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
"""

INDEX = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#16395f">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<title>6S Success Home Micro Zones</title>
<link rel="manifest" href="manifest.webmanifest">
<style>%s</style>
</head><body>
<div id="root"></div>
<script>%s</script>
<script>if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));}</script>
</body></html>""" % (CSS, APP_JS.replace("__DATA__", DATA_JSON))

MANIFEST = json.dumps({
  "name":"6S Success Home Micro Zones: Organization & Housekeeping",
  "short_name":"6S Micro Zones",
  "start_url":".","display":"standalone","background_color":"#f4efe6","theme_color":"#16395f",
  "description":"Reset your home one micro zone at a time. MVP Beta.",
  "icons":[{"src":"icon.svg","sizes":"any","type":"image/svg+xml","purpose":"any maskable"}]
}, indent=2)

SW = """const C='6smz-v0-1';
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(['./','index.html','manifest.webmanifest','icon.svg'])))});
self.addEventListener('activate',e=>{self.clients.claim()});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);
 if(e.request.method!=='GET'||u.origin!==location.origin)return;
 e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{const cp=resp.clone();caches.open(C).then(c=>c.put(e.request,cp));return resp;}).catch(()=>caches.match('index.html'))));});
"""

ICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<rect width="512" height="512" rx="96" fill="#16395f"/>
<text x="256" y="300" font-family="Georgia,serif" font-size="200" font-weight="700" fill="#f4efe6" text-anchor="middle">6S</text>
<circle cx="256" cy="392" r="16" fill="#b8862b"/></svg>"""

os.makedirs(OUTDIR, exist_ok=True)
io.open(os.path.join(OUTDIR, "index.html"), "w", encoding="utf-8").write(INDEX)
io.open(os.path.join(OUTDIR, "manifest.webmanifest"), "w", encoding="utf-8").write(MANIFEST)
io.open(os.path.join(OUTDIR, "sw.js"), "w", encoding="utf-8").write(SW)
io.open(os.path.join(OUTDIR, "icon.svg"), "w", encoding="utf-8").write(ICON)
print("wrote app to:", OUTDIR)
print("index.html bytes:", len(INDEX))
nz = sum(len(r["z"]) for r in data["rooms"])
print("rooms:", len(data["rooms"]), "zones:", nz, "products:", len(data["products"]))
