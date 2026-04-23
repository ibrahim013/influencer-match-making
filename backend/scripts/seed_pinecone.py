#!/usr/bin/env python3
"""
Upsert ~10 demo creator profiles into Pinecone for local / docker testing.

Uses **Pinecone Inference** (`PINECONE_EMBEDDING_MODEL`, default `llama-text-embed-v2`)
via `langchain_pinecone.PineconeEmbeddings` — vectors must match an index compatible
with that model (integrated inference index recommended).

Usage (from backend/):

  cd backend && uv run python scripts/seed_pinecone.py
"""
from __future__ import annotations

import os
import sys

from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from pydantic import SecretStr


def main() -> None:
    pc_key = os.environ.get("PINECONE_API_KEY")
    index_name = os.environ.get("PINECONE_INDEX_NAME", "influencer-creators")
    embed_model = os.environ.get("PINECONE_EMBEDDING_MODEL", "llama-text-embed-v2")
    if not pc_key:
        print("PINECONE_API_KEY is required", file=sys.stderr)
        sys.exit(1)

    creators: list[dict] = [
        {
            "creator_id": "cr_001",
            "handle": "@wellness_ava",
            "niche": "wellness & longevity",
            "follower_count": 185_000,
            "avg_engagement_rate": 0.041,
            "recent_post_topics": "sleep hygiene,magnesium,hydration",
            "audience_geo": "US/CA",
            "text": "Creator @wellness_ava posts about sleep hygiene and hydration for US audiences; 185k followers; strong wellness alignment for supplements.",
        },
        {
            "creator_id": "cr_002",
            "handle": "@chef_luis",
            "niche": "food & beverage",
            "follower_count": 92_000,
            "avg_engagement_rate": 0.058,
            "recent_post_topics": "meal prep,air fryer recipes,latam flavors",
            "audience_geo": "MX/US",
            "text": "Chef Luis shares meal prep and air fryer recipes blending LatAm flavors; 92k followers; great for CPG kitchen brands.",
        },
        {
            "creator_id": "cr_003",
            "handle": "@runwithmia",
            "niche": "running & endurance",
            "follower_count": 240_000,
            "avg_engagement_rate": 0.032,
            "recent_post_topics": "marathon training,shoe reviews,recovery",
            "audience_geo": "UK/EU",
            "text": "Mia documents marathon training and shoe reviews for UK/EU runners; 240k followers; performance apparel fit.",
        },
        {
            "creator_id": "cr_004",
            "handle": "@techie_noms",
            "niche": "consumer tech",
            "follower_count": 410_000,
            "avg_engagement_rate": 0.021,
            "recent_post_topics": "smart home,desk setups,AI gadgets",
            "audience_geo": "US",
            "text": "Consumer tech creator covering smart home and desk setups; 410k US followers; hardware launches.",
        },
        {
            "creator_id": "cr_005",
            "handle": "@eco_jordan",
            "niche": "sustainability",
            "follower_count": 67_000,
            "avg_engagement_rate": 0.072,
            "recent_post_topics": "zero waste,thrifting,ethical fashion",
            "audience_geo": "US",
            "text": "Eco Jordan promotes zero waste and ethical fashion; 67k highly engaged US followers.",
        },
        {
            "creator_id": "cr_006",
            "handle": "@finance_ken",
            "niche": "personal finance",
            "follower_count": 330_000,
            "avg_engagement_rate": 0.019,
            "recent_post_topics": "index funds,credit cards,side hustles",
            "audience_geo": "US",
            "text": "Personal finance educator on index funds and credit card strategy; 330k US followers.",
        },
        {
            "creator_id": "cr_007",
            "handle": "@beauty_sam",
            "niche": "beauty & skincare",
            "follower_count": 150_000,
            "avg_engagement_rate": 0.048,
            "recent_post_topics": "SPF routines,sensitive skin,ingredient breakdowns",
            "audience_geo": "US/UK",
            "text": "Beauty Sam focuses on SPF routines and ingredient science; 150k US/UK followers.",
        },
        {
            "creator_id": "cr_008",
            "handle": "@parenting_taylor",
            "niche": "family & parenting",
            "follower_count": 88_000,
            "avg_engagement_rate": 0.055,
            "recent_post_topics": "toddlers,snack ideas,travel with kids",
            "audience_geo": "US",
            "text": "Parenting Taylor shares toddler snack ideas and family travel tips; 88k US followers.",
        },
        {
            "creator_id": "cr_009",
            "handle": "@indie_dev_alex",
            "niche": "software & startups",
            "follower_count": 55_000,
            "avg_engagement_rate": 0.061,
            "recent_post_topics": "SaaS shipping,API design,founder vlogs",
            "audience_geo": "Global",
            "text": "Indie developer Alex vlogs SaaS shipping and API design; 55k global eng-heavy audience.",
        },
        {
            "creator_id": "cr_010",
            "handle": "@travel_nina",
            "niche": "travel & hospitality",
            "follower_count": 290_000,
            "avg_engagement_rate": 0.027,
            "recent_post_topics": "boutique hotels,solo travel,slow travel",
            "audience_geo": "EU/US",
            "text": "Travel Nina reviews boutique hotels and slow travel itineraries; 290k EU/US followers.",
        },
    ]

    texts = [c.pop("text") for c in creators]
    metadatas = creators

    embeddings = PineconeEmbeddings(
        model=embed_model,
        pinecone_api_key=SecretStr(pc_key),
    )

    PineconeVectorStore.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        index_name=index_name,
        async_req=False,
        pool_threads=1,
    )
    print(f"Upserted {len(texts)} vectors into Pinecone index {index_name!r}.")


if __name__ == "__main__":
    main()
