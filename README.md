# 💰 Clipza Rewards — Clip. Post. Earn. (MVP)

By **JONNY PRODUCTIONS**. The all-in-one clipping rewards platform:

1. **🎬 Clip Studio** — upload any video, smart audio-energy detection finds the
   viral moments, one click cuts vertical 9:16 clips. No ML models, no API keys.
2. **💰 Campaigns** — brands post pay-per-view campaigns (rate per 1,000 views,
   min views, per-clip cap, budget, rules).
3. **📤 Submit & Earn** — clippers submit clips/post links, brands verify views,
   earnings calculate automatically.
4. **🏆 Leaderboard + 📊 Brand Dashboard** — rankings, payouts, review queue.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Demo

Hit **Load demo data** in the sidebar, then run the full loop:
clip → join a campaign → submit → brand approves → leaderboard.

## Notes

- MVP: video files and the SQLite database live on the app's local disk, so
  uploaded clips do not survive a redeploy. A production version would use
  object storage + a hosted database, social-platform APIs for automatic view
  verification, and a real payment provider for payouts.
- Moment detection is audio-energy based (loud, high-intensity sections score
  highest). For AI transcript-based detection, see the standalone
  [Clipza](https://clipza.streamlit.app/) app.
