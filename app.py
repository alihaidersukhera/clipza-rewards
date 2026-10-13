"""Clipza Rewards — the all-in-one clipping rewards platform (MVP).

Cut viral clips from any video, join pay-per-view campaigns, and earn.
By JONNY PRODUCTIONS.
"""
import os
import tempfile

import streamlit as st

import engine
import rewards

rewards.init_db()

st.set_page_config(page_title="Clipza Rewards — Clip. Post. Earn.",
                   page_icon="💰", layout="wide")

# ------------------------------------------------------------------ styles --
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
  .stApp { background: radial-gradient(1200px 600px at 20% -10%, #1c1706 0%, #0b0b0f 55%) fixed; }
  * { font-family: 'Inter', sans-serif !important; }
  .zr-hero { position: relative; overflow: hidden;
    background: linear-gradient(135deg, #14141b 0%, #241c05 60%, #2e2404 100%);
    border: 1px solid #3a3208; border-radius: 22px; padding: 36px 38px; margin-bottom: 20px;
    box-shadow: 0 12px 40px rgba(245,197,24,0.07); }
  .zr-hero::before { content: ""; position: absolute; top: 0; left: -70%; width: 55%; height: 100%;
    background: linear-gradient(105deg, transparent, rgba(255,224,138,0.13), transparent);
    animation: shine 5s ease-in-out infinite; }
  @keyframes shine { 0% { left: -70%; } 55%, 100% { left: 130%; } }
  .zr-hero h1 { position: relative; z-index: 1; margin: 0; font-size: 2.7rem; font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(92deg, #ffe08a, #f5c518 45%, #fff6cf 80%);
    -webkit-background-clip: text; background-clip: text; color: transparent; }
  .zr-hero p { position: relative; z-index: 1; color: #cfcfda; margin: 12px 0 0 0;
    font-size: 1.05rem; line-height: 1.6; }
  .zr-tag { position: relative; z-index: 1; display: inline-block; margin-bottom: 12px;
    background: rgba(245,197,24,0.12); color: #ffd94d; border: 1px solid rgba(245,197,24,0.35);
    font-size: 0.72rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
    border-radius: 999px; padding: 5px 14px; }
  .zr-card { background: linear-gradient(180deg, #16161d, #131318); border: 1px solid #26262f;
    border-radius: 18px; padding: 20px 22px; margin-bottom: 16px;
    transition: border-color .2s, transform .2s; }
  .zr-card:hover { border-color: #4a4210; transform: translateY(-1px); }
  .zr-step { background: linear-gradient(180deg, #191922, #141419); border: 1px solid #2c2c38;
    border-radius: 18px; padding: 22px; text-align: center; height: 100%; }
  .zr-step .n { font-size: 2rem; }
  .zr-step h3 { color: #ffe08a; margin: 10px 0 6px 0; font-size: 1.05rem; }
  .zr-step p { color: #9a9aa5; font-size: 0.9rem; margin: 0; }
  .zr-stat { background: linear-gradient(180deg, #1a1a21, #141419); border: 1px solid #2e2e3a;
    border-radius: 16px; padding: 16px; text-align: center; }
  .zr-stat .v { font-size: 1.7rem; font-weight: 800; color: #ffd94d; }
  .zr-stat .l { color: #9a9aa5; font-size: 0.82rem; margin-top: 4px; }
  .zr-rate { font-size: 1.7rem; font-weight: 800; color: #ffd94d; }
  .zr-meta { color: #9a9aa5; font-size: 0.88rem; }
  .zr-badge { display: inline-block; font-weight: 800; border-radius: 999px;
    padding: 3px 14px; font-size: 0.85rem; }
  .zr-badge.gold { background: linear-gradient(135deg, #ffe08a, #f5c518); color: #161105; }
  .zr-badge.green { background: rgba(46,204,113,0.16); color: #5df08f;
    border: 1px solid rgba(46,204,113,0.45); }
  .zr-badge.blue { background: rgba(93,156,255,0.14); color: #8db8ff;
    border: 1px solid rgba(93,156,255,0.4); }
  .zr-pill { display: inline-block; font-weight: 700; border-radius: 999px;
    padding: 3px 13px; font-size: 0.8rem; }
  .zr-pill.live { background: rgba(46,204,113,0.14); color: #5df08f;
    border: 1px solid rgba(46,204,113,0.45); }
  .zr-pill.paused { background: rgba(255,193,7,0.12); color: #ffd94d;
    border: 1px solid rgba(255,193,7,0.4); }
  .zr-pill.ended { background: rgba(150,150,160,0.12); color: #a9a9b8;
    border: 1px solid rgba(150,150,160,0.35); }
  .zr-pill.pending { background: rgba(93,156,255,0.14); color: #8db8ff;
    border: 1px solid rgba(93,156,255,0.4); }
  .zr-pill.approved { background: rgba(46,204,113,0.14); color: #5df08f;
    border: 1px solid rgba(46,204,113,0.45); }
  .zr-pill.rejected { background: rgba(255,99,99,0.12); color: #ff8f8f;
    border: 1px solid rgba(255,99,99,0.4); }
  .zr-earn { font-size: 1.5rem; font-weight: 800; color: #5df08f; }
  .stButton > button, .stDownloadButton > button { border-radius: 12px; font-weight: 700;
    transition: transform .15s; }
  .stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-1px); }
  .stButton > button[kind="primary"] { background: linear-gradient(135deg, #ffe08a, #f5c518);
    color: #161105; border: none; box-shadow: 0 6px 22px rgba(245,197,24,0.28); }
  .zr-footer { text-align: center; color: #6d6d78; font-size: 0.8rem; margin: 30px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ helpers --
def score_badge(score):
    cls = "gold" if score >= 90 else "green" if score >= 75 else "blue"
    return f"<span class='zr-badge {cls}'>🔥 {score}</span>"


def pill(status):
    return f"<span class='zr-pill {status}'>{status.upper()}</span>"


def tmpdir():
    if "tmpdir" not in st.session_state:
        st.session_state.tmpdir = tempfile.mkdtemp(prefix="clipza_rewards_")
    return st.session_state.tmpdir


def goto(page):
    st.session_state.nav = page
    st.rerun()


# ------------------------------------------------------------------ sidebar --
PAGES = ["🏠 Home", "🎬 Clip Studio", "💰 Campaigns", "📤 Submit & Earn",
         "🏆 Leaderboard", "📊 Brand Dashboard"]
with st.sidebar:
    st.markdown("### 🧭 Clipza Rewards")
    if "nav" not in st.session_state:
        st.session_state.nav = "🏠 Home"
    nav = st.radio("Go to", PAGES, index=PAGES.index(st.session_state.nav),
                   label_visibility="collapsed", key="nav_radio")
    st.session_state.nav = nav
    st.markdown("---")
    st.markdown("**✨ Demo**")
    if st.button("Load demo data"):
        rewards.load_demo_data()
        st.success("Demo campaigns loaded!")
        st.rerun()
    if st.button("Reset all data"):
        rewards.reset_all()
        for k in ("moments", "clips", "video_path"):
            st.session_state.pop(k, None)
        st.rerun()
    st.markdown("---")
    st.markdown("<span class='zr-meta'>Clipza Rewards MVP by<br><b>JONNY PRODUCTIONS</b></span>",
                unsafe_allow_html=True)

page = st.session_state.nav

# -------------------------------------------------------------------- home --
if page == "🏠 Home":
    st.markdown("""
    <div class="zr-hero">
      <span class="zr-tag">Clipping meets pay-per-view rewards</span>
      <h1>💰 Clipza Rewards</h1>
      <p>Upload any video — smart detection finds the viral moments and cuts them into
      <b>9:16 clips</b>. Join brand campaigns, post your clips, and <b>earn for every
      1,000 verified views</b>. One platform, end to end.</p>
    </div>
    """, unsafe_allow_html=True)

    totals = rewards.platform_totals()
    live = rewards.list_campaigns(status="live")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='zr-stat'><div class='v'>{len(live)}</div>"
                    f"<div class='l'>Live campaigns</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='zr-stat'><div class='v'>{totals['views']:,}</div>"
                    f"<div class='l'>Verified views</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='zr-stat'><div class='v'>${totals['paid']:,.2f}</div>"
                    f"<div class='l'>Paid to clippers</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='zr-stat'><div class='v'>{len(rewards.leaderboard())}</div>"
                    f"<div class='l'>Earning creators</div></div>", unsafe_allow_html=True)

    st.markdown("### ⚡ How it works")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown("<div class='zr-step'><div class='n'>🎬</div><h3>1. Clip it</h3>"
                    "<p>Upload a long video. Smart detection finds the best moments "
                    "and cuts vertical clips automatically.</p></div>", unsafe_allow_html=True)
    with s2:
        st.markdown("<div class='zr-step'><div class='n'>💰</div><h3>2. Join a campaign</h3>"
                    "<p>Pick a brand campaign with a rate per 1,000 views. Post your "
                    "clip on TikTok, Shorts or Reels.</p></div>", unsafe_allow_html=True)
    with s3:
        st.markdown("<div class='zr-step'><div class='n'>🏆</div><h3>3. Get paid</h3>"
                    "<p>Submit your post link. The brand verifies views and your "
                    "earnings land on the leaderboard.</p></div>", unsafe_allow_html=True)

    st.markdown("### 🚀 Try the full loop")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("🎬 Start clipping", type="primary", use_container_width=True):
            goto("🎬 Clip Studio")
    with b2:
        if st.button("💰 Browse campaigns", use_container_width=True):
            goto("💰 Campaigns")
    with b3:
        if st.button("📊 I'm a brand", use_container_width=True):
            goto("📊 Brand Dashboard")
    st.markdown("<span class='zr-meta'>👆 New here? Hit <b>Load demo data</b> in the sidebar, "
                "then run the loop: clip → join → submit → earn.</span>", unsafe_allow_html=True)

# ------------------------------------------------------------- clip studio --
elif page == "🎬 Clip Studio":
    st.markdown("## 🎬 Clip Studio")
    st.markdown("<span class='zr-meta'>Upload a video → detect viral moments → cut 9:16 clips → "
                "submit them straight into a campaign.</span>", unsafe_allow_html=True)

    up = st.file_uploader("Upload your video", type=["mp4", "mov", "webm", "mkv"])
    if up:
        vpath = os.path.join(tmpdir(), up.name)
        if st.session_state.get("video_path") != vpath or not os.path.exists(vpath):
            with open(vpath, "wb") as f:
                f.write(up.getbuffer())
            st.session_state.video_path = vpath
            for k in ("moments", "clips", "duration"):
                st.session_state.pop(k, None)
        try:
            dur = st.session_state.get("duration") or engine.video_duration(vpath)
            st.session_state.duration = dur
        except RuntimeError as e:
            st.error(str(e))
            st.stop()
        st.video(vpath)
        st.markdown(f"<span class='zr-meta'>⏱ {engine.fmt_time(dur)} long</span>",
                    unsafe_allow_html=True)

        if st.button("🔍 Find viral moments", type="primary"):
            with st.spinner("Analyzing audio energy to find the hottest moments…"):
                try:
                    st.session_state.moments = engine.detect_moments(vpath, count=5)
                    st.session_state.clips = []
                except RuntimeError as e:
                    st.error(str(e))
                    st.stop()

    moments = st.session_state.get("moments", [])
    if moments:
        st.markdown("### ✨ Detected moments — tick the ones you want")
        sel = []
        for i, m in enumerate(moments):
            key = f"m_{i}"
            with st.container():
                c1, c2 = st.columns([1, 5])
                with c1:
                    checked = st.checkbox("Select", value=True, key=key)
                with c2:
                    st.markdown(f"""
                    <div class="zr-card">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b>Moment {i + 1} — {engine.fmt_time(m['start'])} → {engine.fmt_time(m['end'])}</b>
                        {score_badge(m['score'])}
                      </div>
                      <div class="zr-meta" style="margin-top:6px;">{m['reason']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                if checked:
                    sel.append((i, m))
        if sel and st.button(f"✂️ Cut {len(sel)} clip{'s' if len(sel) > 1 else ''}",
                             type="primary"):
            clips = []
            bar = st.progress(0)
            for j, (i, m) in enumerate(sel):
                out = os.path.join(tmpdir(), f"clip_{i + 1}_{int(m['start'])}s.mp4")
                with st.spinner(f"Cutting clip {j + 1}/{len(sel)}…"):
                    engine.cut_clip(st.session_state.video_path, m["start"],
                                    m["end"], out)
                clips.append({"path": out, "moment": m, "idx": i + 1})
                bar.progress((j + 1) / len(sel))
            st.session_state.clips = clips
            st.success(f"{len(clips)} clip{'s' if len(clips) > 1 else ''} ready! 🎉")

    clips = st.session_state.get("clips", [])
    if clips:
        st.markdown("### 🎞 Your clips")
        live_camps = rewards.list_campaigns(status="live")
        for c in clips:
            with st.container():
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.video(c["path"])
                with c2:
                    m = c["moment"]
                    st.markdown(f"**Clip {c['idx']}** {score_badge(m['score'])}<br>"
                                f"<span class='zr-meta'>{engine.fmt_time(m['start'])} → "
                                f"{engine.fmt_time(m['end'])} • 720×1280 vertical</span>",
                                unsafe_allow_html=True)
                    with open(c["path"], "rb") as f:
                        st.download_button("⬇️ Download", f,
                                           file_name=os.path.basename(c["path"]),
                                           key=f"dl_{c['idx']}")
                    if live_camps:
                        camp_names = [f"#{cp['id']} — {cp['name']} "
                                      f"(${cp['rate_per_1k']:.2f}/1k)" for cp in live_camps]
                        pick = st.selectbox("Submit to campaign", camp_names,
                                            key=f"camp_{c['idx']}")
                        cname = st.text_input("Your clipper name",
                                              key=f"cn_{c['idx']}")
                        if st.button("💰 Submit this clip", key=f"sub_{c['idx']}"):
                            cid = int(pick.split(" — ")[0][1:])
                            if not cname:
                                st.warning("Enter your clipper name first.")
                            else:
                                sid = rewards.submit_clip(
                                    cid, cname, "TikTok",
                                    "(clip submitted from Clip Studio — add post link after posting)",
                                    0, clip_path=c["path"])
                                st.success(f"Submitted as **#{sid}**! Post it on TikTok/Shorts/Reels, "
                                           f"then update the link from 📤 Submit & Earn.")
                    else:
                        st.info("No live campaigns — create one from 💰 Campaigns.")

# --------------------------------------------------------------- campaigns --
elif page == "💰 Campaigns":
    tab1, tab2 = st.tabs(["🔍 Browse", "➕ Create (brands)"])
    with tab1:
        st.markdown("## Live campaigns")
        campaigns = rewards.list_campaigns()
        if not campaigns:
            st.info("No campaigns yet. Brands can create one in the **Create** tab — "
                    "or load demo data from the sidebar.")
        for c in campaigns:
            stats = rewards.campaign_stats(c["id"])
            cap = f"{c['cap_per_clip']:,}" if c["cap_per_clip"] else "No cap"
            st.markdown(f"""
            <div class="zr-card">
              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div><b style="font-size:1.15rem;">{c['name']}</b><br>
                <span class="zr-meta">by {c['brand_name']}</span></div>
                <div style="text-align:right;"><div class="zr-rate">${c['rate_per_1k']:.2f}</div>
                <span class="zr-meta">per 1,000 views</span></div>
              </div>
              <div style="margin-top:10px;"><span class="zr-meta">Min views: <b>{c['min_views']:,}</b></span>
              &nbsp;•&nbsp; <span class="zr-meta">Cap per clip: <b>{cap}</b></span>
              &nbsp;•&nbsp; <span class="zr-meta">Budget left: <b>${stats['remaining'] if stats['remaining'] is not None else '—'}</b></span>
              &nbsp; {pill(c['status'])}</div>
              {f"<div class='zr-card' style='margin:10px 0 0 0; padding:12px 16px;'><span class='zr-meta' style='white-space:pre-line;'>{c['rules']}</span></div>" if c['rules'] else ""}
              <div class="zr-meta" style="margin-top:8px;">👁 {stats['total_views']:,} verified views •
              {stats['submissions']} submissions • ${stats['spent']:.2f} paid out</div>
            </div>
            """, unsafe_allow_html=True)
            if c["status"] == "live" and st.button(f"💰 Join — {c['name']}",
                                                  key=f"join_{c['id']}"):
                st.session_state.join_campaign = c["id"]
                goto("📤 Submit & Earn")
    with tab2:
        st.markdown("## Create a campaign")
        with st.form("new_campaign"):
            name = st.text_input("Campaign name", placeholder="e.g. Summer Launch Clips")
            brand = st.text_input("Brand / company name")
            c1, c2 = st.columns(2)
            with c1:
                rate = st.number_input("Rate per 1,000 views ($)", 0.1, 100.0, 1.5, 0.1)
                min_views = st.number_input("Minimum views to count", 0, 1000000, 1000, 100)
            with c2:
                cap = st.number_input("Cap per clip (views, 0 = no cap)", 0, 100000000, 0, 1000)
                budget = st.number_input("Total budget ($, 0 = unlimited)", 0.0, 1000000.0, 500.0, 10.0)
            rules = st.text_area("Campaign rules (one per line)",
                                 placeholder="1. Clip must come from the source video…\n2. Minimum 10 seconds…")
            if st.form_submit_button("🚀 Launch campaign", type="primary"):
                if not name or not brand:
                    st.warning("Campaign name and brand name are required.")
                else:
                    cid = rewards.create_campaign(name, brand, rate, min_views,
                                                  cap, budget, rules)
                    st.success(f"Campaign **#{cid} — {name}** is live! 🎉")

# ------------------------------------------------------------ submit & earn --
elif page == "📤 Submit & Earn":
    tab1, tab2 = st.tabs(["📤 Submit a clip", "💵 My earnings"])
    with tab1:
        st.markdown("## Submit your clip")
        campaigns = rewards.list_campaigns(status="live")
        if not campaigns:
            st.info("No live campaigns right now — check back soon, or load demo data.")
        else:
            cmap = {f"#{c['id']} — {c['name']} (${c['rate_per_1k']:.2f}/1k views)": c
                    for c in campaigns}
            defkey = None
            jc = st.session_state.pop("join_campaign", None)
            if jc:
                for k, c in cmap.items():
                    if c["id"] == jc:
                        defkey = k
            sel = st.selectbox("Campaign", list(cmap.keys()),
                               index=list(cmap.keys()).index(defkey) if defkey else 0)
            c = cmap[sel]
            st.markdown(f"<span class='zr-meta'>Min {c['min_views']:,} views to count • "
                        f"Brand: {c['brand_name']}</span>", unsafe_allow_html=True)
            with st.form("submit"):
                clipper = st.text_input("Your clipper name")
                platform = st.selectbox("Platform", ["TikTok", "YouTube Shorts",
                                                     "Instagram Reels"])
                url = st.text_input("Link to your posted clip")
                views = st.number_input("Current views on the post", 0, 1000000000, 0, 100)
                if st.form_submit_button("📤 Submit for review", type="primary"):
                    if not clipper or not url:
                        st.warning("Clipper name and post link are required.")
                    else:
                        sid = rewards.submit_clip(c["id"], clipper, platform,
                                                  url, views)
                        st.success(f"Submitted as **#{sid}**! The brand verifies views — "
                                   f"payment lands after approval. 💸")
    with tab2:
        st.markdown("## My earnings")
        name = st.text_input("Enter your clipper name")
        if name:
            subs = rewards.list_submissions(clipper=name)
            if not subs:
                st.info("No submissions found for this name yet.")
            else:
                total = round(sum(s["earnings"] for s in subs), 2)
                views = sum(s["verified_views"] for s in subs)
                e1, e2 = st.columns(2)
                with e1:
                    st.markdown(f"<div class='zr-stat'><div class='v'>${total:.2f}</div>"
                                f"<div class='l'>Total earned</div></div>", unsafe_allow_html=True)
                with e2:
                    st.markdown(f"<div class='zr-stat'><div class='v'>{views:,}</div>"
                                f"<div class='l'>Verified views</div></div>", unsafe_allow_html=True)
                for s in subs:
                    camp = rewards.get_campaign(s["campaign_id"]) or {}
                    st.markdown(f"{pill(s['status'])} #{s['id']} — {camp.get('name', '?')} • "
                                f"{s['platform']} • {s['verified_views']:,} verified views • "
                                f"**${s['earnings']:.2f}**")

# -------------------------------------------------------------- leaderboard --
elif page == "🏆 Leaderboard":
    st.markdown("## 🏆 Top clippers")
    board = rewards.leaderboard()
    if not board:
        st.info("No approved submissions yet — the leaderboard is empty. Load demo data to see it in action!")
    for i, row in enumerate(board, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"#{i}")
        st.markdown(f"""
        <div class="zr-card">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div><b style="font-size:1.1rem;">{medal} {row['clipper_name']}</b><br>
            <span class="zr-meta">{row['clips']} approved clips • {row['views']:,} verified views</span></div>
            <div class="zr-earn">${row['earnings']:.2f}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------- brand dashboard --
else:
    st.markdown("## 📊 Brand Dashboard")
    campaigns = rewards.list_campaigns()
    if not campaigns:
        st.info("No campaigns yet — create one from 💰 Campaigns → Create, or load demo data.")
    else:
        cmap = {f"#{c['id']} — {c['name']}": c["id"] for c in campaigns}
        sel = st.selectbox("Campaign", list(cmap.keys()))
        cid = cmap[sel]
        camp = rewards.get_campaign(cid)
        stats = rewards.campaign_stats(cid)
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"<div class='zr-stat'><div class='v'>{stats['submissions']}</div>"
                        f"<div class='l'>Submissions</div></div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='zr-stat'><div class='v'>{stats['total_views']:,}</div>"
                        f"<div class='l'>Verified views</div></div>", unsafe_allow_html=True)
        with k3:
            st.markdown(f"<div class='zr-stat'><div class='v'>${stats['spent']:.2f}</div>"
                        f"<div class='l'>Paid out</div></div>", unsafe_allow_html=True)
        with k4:
            left = f"${stats['remaining']:.2f}" if stats["remaining"] is not None else "∞"
            st.markdown(f"<div class='zr-stat'><div class='v'>{left}</div>"
                        f"<div class='l'>Budget left</div></div>", unsafe_allow_html=True)

        st.markdown("### 📥 Review queue")
        pending = rewards.list_submissions(campaign_id=cid, status="pending")
        if not pending:
            st.info("Nothing waiting — the queue is clear. ✅")
        for s in pending:
            with st.expander(f"#{s['id']} — {s['clipper_name']} • {s['platform']} • "
                             f"{s['reported_views']:,} reported views"):
                if s["clip_path"] and os.path.exists(s["clip_path"]):
                    st.video(s["clip_path"])
                if s["post_url"] and s["post_url"].startswith("http"):
                    st.markdown(f"🔗 [Open post]({s['post_url']})")
                else:
                    st.markdown(f"<span class='zr-meta'>{s['post_url']}</span>",
                                unsafe_allow_html=True)
                st.markdown(f"<span class='zr-meta'>Payout if approved: verified views ÷ 1,000 × "
                            f"${camp['rate_per_1k']:.2f} (min {camp['min_views']:,} views)</span>",
                            unsafe_allow_html=True)
                v1, v2 = st.columns(2)
                with v1:
                    vv = st.number_input("Verified views", 0, 1000000000,
                                         s["reported_views"], 100, key=f"vv_{s['id']}")
                with v2:
                    st.write("")
                    st.write("")
                    ok = st.button("✅ Approve & pay", key=f"ok_{s['id']}")
                    no = st.button("❌ Reject", key=f"no_{s['id']}")
                if ok:
                    earn = rewards.review_submission(s["id"], vv, approve=True)
                    st.success(f"Approved — {s['clipper_name']} earns **${earn:.2f}**. 💸")
                    st.rerun()
                if no:
                    rewards.review_submission(s["id"], vv, approve=False)
                    st.warning("Rejected.")
                    st.rerun()

        done = [s for s in rewards.list_submissions(campaign_id=cid)
                if s["status"] != "pending"]
        if done:
            st.markdown("### ✅ Decided")
            for s in done:
                st.markdown(f"{pill(s['status'])} #{s['id']} — {s['clipper_name']} • "
                            f"{s['verified_views']:,} views • **${s['earnings']:.2f}**")

        st.markdown("---")
        b1, b2, b3 = st.columns(3)
        with b1:
            if camp["status"] == "live" and st.button("⏸ Pause campaign"):
                rewards.set_campaign_status(cid, "paused")
                st.rerun()
        with b2:
            if camp["status"] == "paused" and st.button("▶ Resume campaign"):
                rewards.set_campaign_status(cid, "live")
                st.rerun()
        with b3:
            if camp["status"] != "ended" and st.button("⏹ End campaign"):
                rewards.set_campaign_status(cid, "ended")
                st.rerun()

st.markdown("<div class='zr-footer'>💰 <b>Clipza Rewards</b> MVP by <b>JONNY PRODUCTIONS</b> • "
            "Clip. Post. Earn.</div>", unsafe_allow_html=True)
