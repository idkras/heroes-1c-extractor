#!/usr/bin/env python3
"""
Test Ilya Krasinsky Review Standard on seller24 review
"""

import sys
import json
sys.path.append('/home/runner/workspace')

from advising_platform.src.mcp.python_backends.ilya_review_challenge import handle_ilya_review_challenge
import asyncio

async def test_seller24_review():
    # Read the seller24 review content
    with open('advising_platform/[projects]/[heroes-gpt-bot]/review-results/seller24_platform_landing_review_by_heroesGPT_bot.md', 'r', encoding='utf-8') as f:
        seller24_content = f.read()
    
    # Apply Ilya Krasinsky Review Challenge
    args = {
        "document_content": seller24_content,
        "document_type": "landing_review",
        "focus_areas": ["user_centric", "segment_gaps", "no_tasks", "trust_issues"]
    }
    
    result = await handle_ilya_review_challenge(args)
    
    if result["success"]:
        print("✅ Ilya Krasinsky Review applied successfully!")
        print(f"Quality Score: {result['analysis']['quality_score']:.1f}/10")
        print(f"Challenge Areas Found: {len(result['analysis']['challenge_areas'])}")
        
        # Save enhanced review with Ilya's comments
        with open('advising_platform/seller24_review_with_ilya_comments.md', 'w', encoding='utf-8') as f:
            f.write(result["enhanced_content"])
        
        print("\n📄 Enhanced review saved to: seller24_review_with_ilya_comments.md")
        
        # Show sample of Ilya's comments
        for i, challenge in enumerate(result['analysis']['challenge_areas'][:3]):
            print(f"\n💭 Challenge {i+1}: {challenge['type']}")
            print(f"   Comment: {challenge['comment'][:100]}...")
            
    else:
        print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_seller24_review())