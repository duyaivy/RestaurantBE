# VietFood Stories Dataset for RAG (English-first scenario library)

> This file contains scenario-driven retrieval content for a restaurant chatbot. Each story is designed to help the assistant answer intent-heavy questions from foreign guests, mixed-language users, and recommendation requests that are not simple exact dish matches.

## How to use this file

- Each story is a semantic chunk for recommendation-style retrieval.
- English is written first because the target audience includes foreign visitors.
- Vietnamese query examples are included to support mixed-language search.
- `recommended_items` intentionally reuse exact database dish names so the assistant can bridge stories to live menu items.

## S001 — First-time tourist wants one iconic local meal

- **persona:** Foreign tourist, first day in Da Nang, curious but cautious
- **situation:** The guest wants something recognizably Vietnamese, not too hard to approach, and preferably connected to Central Vietnam.
- **sample_queries_en:** What should I eat here if it's my first time in Vietnam? | I want something local but not too weird. | What dish feels like Da Nang or Central Vietnam?
- **sample_queries_vi:** Lần đầu ăn ở đây thì nên gọi gì? | Mình muốn món địa phương nhưng dễ ăn.
- **recommended_items:** Quang Noodle (Mì Quảng), Hoi An Chicken Rice (Cơm gà Hội An), Fresh Spring Rolls, Orange Juice (Nước cam)
- **why_this_works:** Quang Noodle and Hoi An Chicken Rice carry a clear Central Vietnam identity, while Fresh Spring Rolls and Orange Juice make the meal feel light and friendly.
- **answer_style:** Warm, informative, beginner-friendly. Explain dish names in English first and add Vietnamese names in parentheses.
- **retrieval_tags:** tourist, first_time, central_vietnam, beginner_friendly, english_support

## S002 — Solo budget lunch under 100,000 VND

- **persona:** Student or office worker eating alone
- **situation:** The guest wants one filling dish and one low-cost drink without overspending.
- **sample_queries_en:** Can I have a full meal for under 100k? | What's a cheap but filling lunch?
- **sample_queries_vi:** Dưới 100k thì ăn gì no? | Có combo nào rẻ mà ổn không?
- **recommended_items:** Beef Pho (Phở bò), Vietnamese Baguette Sandwich (Bánh mì), Water (Nước lọc), Pepsi (Pepsi)
- **why_this_works:** Beef Pho is filling, Vietnamese Baguette Sandwich is budget-friendly, and Water or Pepsi keep the order simple.
- **answer_style:** Fast, practical, numbers-first. Mention prices clearly.
- **retrieval_tags:** budget, solo, lunch, affordable, quick_meal

## S003 — Guest wants mild food with no strong chili

- **persona:** Cautious eater, family traveler, or child-friendly request
- **situation:** The guest wants comfort food, low spice, and familiar textures.
- **sample_queries_en:** I don't eat spicy food. What do you recommend? | What's the safest mild dish here?
- **sample_queries_vi:** Mình không ăn cay, gợi ý món nào? | Có món nào dễ ăn không?
- **recommended_items:** Beef Pho (Phở bò), Hoi An Chicken Rice (Cơm gà Hội An), Tofu with Scallion Oil (Đậu tẩm hành), Orange Juice (Nước cam)
- **why_this_works:** These dishes are calmer in flavor and can be described without complex seasoning.
- **answer_style:** Reassuring and gentle. Avoid recommending satay, Thai-style broth, or heavy chili notes.
- **retrieval_tags:** non_spicy, mild, family_friendly, safe_choice

## S004 — Friends gathering for grilled food and beer

- **persona:** Young adults dining in the evening
- **situation:** The group wants lively flavors, sharing dishes, and a casual social dinner.
- **sample_queries_en:** What's good with beer? | We want grilled dishes for sharing.
- **sample_queries_vi:** Có món gì hợp nhậu? | Nhóm mình muốn ăn món nướng.
- **recommended_items:** BBQ Grilled Pork Ribs, Grilled Squid with Satay (Mực nướng sa tế), Grilled Chicken Feet (Chân gà nướng), Beer (Bia)
- **why_this_works:** These dishes create a social, savory, evening-dining mood and pair naturally with Beer.
- **answer_style:** Energetic and social. Emphasize sharing and pairing.
- **retrieval_tags:** group, grilled, beer, evening, sharing

## S005 — Customer asks for a seafood-heavy dinner

- **persona:** Visitor who came to Da Nang expecting seafood
- **situation:** The guest wants seafood that feels worth the trip, preferably shareable.
- **sample_queries_en:** What seafood should I order? | I want a seafood dinner in Da Nang.
- **sample_queries_vi:** Nên gọi hải sản gì? | Muốn ăn tối thiên về hải sản thì sao?
- **recommended_items:** Tamarind Fried Crab (Cua rang me), Grilled Oysters with Scallion Oil (Hào nướng mỡ hành), Thai-Style Steamed Clams (Nghêu hấp Thái), Steamed Shrimp with Lemongrass (Tôm hấp sả)
- **why_this_works:** This mix covers rich, saucy, aromatic, and lighter seafood options.
- **answer_style:** Confident and appetizing. Use sensory language like tangy, smoky, aromatic, fresh.
- **retrieval_tags:** seafood, da_nang, dinner, group_sharing

## S006 — Family with children wants easy dishes

- **persona:** Parents dining with kids or older relatives
- **situation:** The table needs familiar, not-too-spicy dishes with flexible portions.
- **sample_queries_en:** What should a family with kids order? | Any dishes that are easy for children?
- **sample_queries_vi:** Nhà có trẻ em thì gọi gì? | Có món nào người lớn tuổi cũng dễ ăn không?
- **recommended_items:** Hoi An Chicken Rice (Cơm gà Hội An), Yangzhou Fried Rice (Cơm chiên Dương Châu), Broken Rice with Grilled Pork Chop (Cơm tấm sườn), Water (Nước lọc), Orange Juice (Nước cam)
- **why_this_works:** Rice-based dishes are familiar, filling, and easy to share or portion out.
- **answer_style:** Calm, family-oriented, practical.
- **retrieval_tags:** family, children, easy_food, rice_dishes

## S007 — Guest wants a clearly Central Vietnam recommendation

- **persona:** Food-motivated traveler
- **situation:** The guest specifically wants dishes tied to the region instead of generic Vietnamese food.
- **sample_queries_en:** What is the most Central Vietnamese dish on the menu? | Give me something from this region.
- **sample_queries_vi:** Món nào đậm chất miền Trung nhất? | Cho mình món đúng kiểu vùng này.
- **recommended_items:** Quang Noodle (Mì Quảng), Hoi An Chicken Rice (Cơm gà Hội An), Hue Beef Noodle Soup (Bún bò Huế), Chicken Hotpot with Basil (Lẩu gà lá é)
- **why_this_works:** These dishes feel geographically grounded and strengthen the restaurant identity.
- **answer_style:** Cultural but concise. Avoid over-explaining unless asked.
- **retrieval_tags:** regional, central_vietnam, authenticity, local_food

## S008 — Rainy-day comfort food request

- **persona:** Guest wants warmth and comfort
- **situation:** It is rainy, cool, or the guest simply wants broth and warmth.
- **sample_queries_en:** What's good on a rainy day? | I want something warm and comforting.
- **sample_queries_vi:** Trời mưa nên ăn gì? | Mình muốn món ấm bụng.
- **recommended_items:** Beef Pho (Phở bò), Hue Beef Noodle Soup (Bún bò Huế), Crab Tomato Vermicelli Soup (Bún riêu), Beef Hotpot (Lẩu bò)
- **why_this_works:** Brothy noodle dishes and hotpot work well for emotional comfort and weather-based prompts.
- **answer_style:** Cozy and descriptive.
- **retrieval_tags:** rainy_day, comfort_food, soup, hotpot

## S009 — Light meal for a casual date or gentle dinner

- **persona:** Couple or two friends wanting a neat dinner
- **situation:** The table wants something tasty but not too heavy.
- **sample_queries_en:** We want a lighter dinner for two. | Something nice but not too heavy?
- **sample_queries_vi:** Tụi mình muốn ăn tối nhẹ nhàng. | Có món nào ngon mà không quá nặng bụng không?
- **recommended_items:** Fresh Spring Rolls, Tofu with Scallion Oil (Đậu tẩm hành), Steamed Shrimp with Lemongrass (Tôm hấp sả), Orange Juice (Nước cam)
- **why_this_works:** These dishes feel cleaner, lighter, and more elegant than a hotpot or a full grilled spread.
- **answer_style:** Soft and polished.
- **retrieval_tags:** date_night, light_meal, two_people, elegant

## S010 — Guest wants the restaurant's signature identity in one table

- **persona:** Curious diner asking for the 'most VietFood' experience
- **situation:** The goal is to build a table that reflects the restaurant’s story and positioning.
- **sample_queries_en:** What order best represents VietFood? | Give me a table that feels most like this restaurant.
- **sample_queries_vi:** Gọi món nào để ra chất VietFood nhất? | Muốn trải nghiệm đúng tinh thần quán thì gọi gì?
- **recommended_items:** Fresh Spring Rolls, Quang Noodle (Mì Quảng), Hoi An Chicken Rice (Cơm gà Hội An), Grilled Beef in Betel Leaves (Bò nướng lá lốt), Orange Juice (Nước cam)
- **why_this_works:** This set blends approachable starters, Central Vietnamese staples, and a dish with strong local dining character.
- **answer_style:** Brand-aware and slightly emotional.
- **retrieval_tags:** signature, brand_identity, representative_order

## S011 — Office lunch for two colleagues

- **persona:** Two coworkers with limited time
- **situation:** They want a fast, balanced lunch that does not feel too messy or too expensive.
- **sample_queries_en:** Lunch for two, quick and good? | We only have about 30 minutes.
- **sample_queries_vi:** Ăn trưa nhanh cho 2 người thì gọi gì? | Bọn mình không có nhiều thời gian.
- **recommended_items:** Broken Rice with Grilled Pork Chop (Cơm tấm sườn), Beef Pho (Phở bò), Pepsi (Pepsi), Water (Nước lọc)
- **why_this_works:** Both mains are reliable and easy to explain. The drinks keep the order simple.
- **answer_style:** Efficient and practical.
- **retrieval_tags:** office_lunch, fast_service, two_people, practical

## S012 — Customer wants crispy textures and fried items

- **persona:** Guest who likes crunchy food
- **situation:** The guest is drawn to crisp textures and snackable starters.
- **sample_queries_en:** I want something crispy. | What fried or crunchy dishes do you have?
- **sample_queries_vi:** Mình thích món giòn. | Có món chiên hay giòn không?
- **recommended_items:** Fried Spring Roll, Vietnamese Crispy Pancake (Bánh xèo), Tofu with Scallion Oil (Đậu tẩm hành)
- **why_this_works:** Fried Spring Roll gives a clear crunchy bite, Vietnamese Crispy Pancake adds a classic Vietnamese texture, and Tofu with Scallion Oil offers a softer crisp.
- **answer_style:** Texture-focused and vivid.
- **retrieval_tags:** crispy, fried, crunchy, starter

## S013 — Hotpot recommendation for a hungry group

- **persona:** Group dinner, appetite is high
- **situation:** The group wants a centerpiece dish that feels communal.
- **sample_queries_en:** Which hotpot should we get? | We're a group and want something shared.
- **sample_queries_vi:** Nên gọi lẩu nào? | Nhóm mình muốn món ăn chung.
- **recommended_items:** Chicken Hotpot with Basil (Lẩu gà lá é), Beef Hotpot (Lẩu bò), Crab Paste Hotpot (Lẩu riêu cua), Water (Nước lọc), Beer (Bia)
- **why_this_works:** These hotpots create a shared dining ritual and work for 2–4 people depending on side dishes.
- **answer_style:** Group-oriented and clear about portion expectations.
- **retrieval_tags:** hotpot, group, centerpiece, sharing

## S014 — Guest asks for rice instead of noodles

- **persona:** Traveler not in the mood for soup
- **situation:** The guest wants rice dishes and a filling plate-style meal.
- **sample_queries_en:** I want rice, not noodles. | What are your best rice dishes?
- **sample_queries_vi:** Mình muốn ăn cơm chứ không ăn bún phở. | Món cơm nào ngon?
- **recommended_items:** Hoi An Chicken Rice (Cơm gà Hội An), Broken Rice with Grilled Pork Chop (Cơm tấm sườn), Yangzhou Fried Rice (Cơm chiên Dương Châu), Braised Pork with Eggs (Thịt kho tàu)
- **why_this_works:** These dishes cover local-style rice, a classic pork plate, fried rice, and a home-style braise.
- **answer_style:** Straightforward and preference-matching.
- **retrieval_tags:** rice_dishes, not_noodles, filling_meal

## S015 — Guest wants home-style Vietnamese comfort

- **persona:** Traveler or local craving familiar home food
- **situation:** The guest wants food that feels like a family meal rather than street snacks.
- **sample_queries_en:** What feels like home-style Vietnamese food? | I want a family-meal kind of dish.
- **sample_queries_vi:** Có món nào kiểu cơm nhà không? | Muốn món giống bữa cơm gia đình.
- **recommended_items:** Braised Pork with Eggs (Thịt kho tàu), Braised Fish in Clay Pot (Cá kho tộ), Stir-Fried Morning Glory with Garlic (Rau muống xào tỏi), Water (Nước lọc)
- **why_this_works:** These dishes feel closest to a traditional home-cooked table.
- **answer_style:** Warm and nostalgic.
- **retrieval_tags:** home_style, family_meal, comfort, vietnamese_classic

## S016 — Guest wants something good with beer but not too expensive

- **persona:** Budget-conscious evening diner
- **situation:** The guest wants a social snack-and-drink pattern without ordering premium crab or hotpot.
- **sample_queries_en:** What's good with beer on a budget? | I want a cheap evening order.
- **sample_queries_vi:** Món nào hợp bia mà không quá đắt? | Muốn ăn tối kiểu nhẹ nhẹ tiết kiệm.
- **recommended_items:** Grilled Chicken Feet (Chân gà nướng), Fried Spring Roll, BBQ Grilled Pork Ribs, Beer (Bia)
- **why_this_works:** These choices balance affordability, shareability, and a casual drinking mood.
- **answer_style:** Casual and street-smart.
- **retrieval_tags:** beer_food, budget_evening, casual

## S017 — Customer asks for the safest recommendation for foreign beginners

- **persona:** International guest unfamiliar with Vietnamese names
- **situation:** The assistant should reduce friction and avoid overwhelming explanations.
- **sample_queries_en:** I don't know Vietnamese food. What is the safest dish? | Please recommend something easy for foreigners.
- **sample_queries_vi:** Khách nước ngoài mới ăn thì chọn món nào an toàn?
- **recommended_items:** Beef Pho (Phở bò), Fresh Spring Rolls, Hoi An Chicken Rice (Cơm gà Hội An), Orange Juice (Nước cam)
- **why_this_works:** These dishes are easy to describe, recognizable, and low-friction for newcomers.
- **answer_style:** Simple English, friendly reassurance, minimal jargon.
- **retrieval_tags:** foreign_guest, english, safe_choice, beginner

## S018 — Customer wants to know the founder story

- **persona:** Guest interested in the people behind the restaurant
- **situation:** The guest is not just asking about food; they want a human connection.
- **sample_queries_en:** Who started this restaurant? | What's the story behind VietFood?
- **sample_queries_vi:** Ai mở quán này? | Câu chuyện của VietFood là gì?
- **recommended_items:** Quang Noodle (Mì Quảng), Hoi An Chicken Rice (Cơm gà Hội An)
- **why_this_works:** These dishes support the founder story because they feel regional, grounded, and family-linked.
- **answer_style:** Narrative, warm, proud but not exaggerated.
- **retrieval_tags:** owner_story, brand_story, emotional_context

## S019 — Guest wants seafood but no heavy sauce

- **persona:** Health-conscious or clean-flavor preference
- **situation:** The guest likes seafood but wants a lighter preparation.
- **sample_queries_en:** I want seafood but not too heavy. | Any lighter seafood dishes?
- **sample_queries_vi:** Muốn ăn hải sản mà nhẹ vị thôi. | Có món hải sản nào thanh hơn không?
- **recommended_items:** Steamed Shrimp with Lemongrass (Tôm hấp sả), Grilled Oysters with Scallion Oil (Hào nướng mỡ hành), Orange Juice (Nước cam), Water (Nước lọc)
- **why_this_works:** These options feel cleaner than tamarind crab while still tasting distinctly seaside and Vietnamese.
- **answer_style:** Fresh, light, and health-aware.
- **retrieval_tags:** light_seafood, clean_flavors, healthy_feel

## S020 — Guest asks what to order for a mixed table with different tastes

- **persona:** Group with one spicy eater, one mild eater, and one seafood lover
- **situation:** The assistant must build a balanced table that satisfies different preferences.
- **sample_queries_en:** We all want different things. What should we order? | Can you suggest a balanced table?
- **sample_queries_vi:** Mỗi người thích một kiểu thì gọi sao? | Gợi ý bàn ăn cân bằng giúp mình.
- **recommended_items:** Fresh Spring Rolls, Beef Pho (Phở bò), Grilled Shrimp with Chili Salt (Tôm nướng muối ớt), Stir-Fried Morning Glory with Garlic (Rau muống xào tỏi), Orange Juice (Nước cam), Beer (Bia)
- **why_this_works:** This spread covers light, mild, spicy, vegetable, and drink preferences without becoming too expensive or too chaotic.
- **answer_style:** Structured and diplomatic. Explain why each dish covers a different need.
- **retrieval_tags:** mixed_group, balanced_order, varied_preferences

## Optional system behavior hints

- When a foreign guest seems unsure, recommend one starter, one main dish, and one drink rather than listing too many items.
- When a query is broad, prefer Central Vietnam identity dishes first: Quang Noodle, Hoi An Chicken Rice, Hue Beef Noodle Soup, Chicken Hotpot with Basil.
- When a query is budget-sensitive, mention prices clearly in VND and optionally add approximate USD.
- When a guest asks about allergies, do not overpromise. Suggest confirming directly with staff.
- When the request is emotional or story-based, mention the family-rooted origin of VietFood and founder Nguyễn Quốc Duy.

## Exact available menu references

## Appetizers / Khai vị

- **Fried Spring Roll** (`db_name_en: Spring roll` | `db_name_vi: Chả giò`) — 30,000 VND (~$1.20)
- **Fresh Spring Rolls** (`db_name_en: Spring rolls` | `db_name_vi: Gỏi cuốn`) — 30,000 VND (~$1.20)
- **Tofu with Scallion Oil (Đậu tẩm hành)** (`db_name_en: Tofu with scallions` | `db_name_vi: Đậu tẩm hành`) — 40,000 VND (~$1.60)

## Main Dishes / Món chính

- **Vietnamese Baguette Sandwich (Bánh mì)** (`db_name_en: Vietnamese Baguette Sandwich` | `db_name_vi: Bánh mì`) — 25,000 VND (~$1.00)
- **Stir-Fried Morning Glory with Garlic (Rau muống xào tỏi)** (`db_name_en: Stir Fried Morning Glory with Garlic` | `db_name_vi: Rau muống xào tỏi`) — 30,000 VND (~$1.20)
- **Vietnamese Crispy Pancake (Bánh xèo)** (`db_name_en: Vietnamese Crispy Pancake` | `db_name_vi: Bánh xèo`) — 40,000 VND (~$1.60)
- **Yangzhou Fried Rice (Cơm chiên Dương Châu)** (`db_name_en: Yangzhou Fried Rice` | `db_name_vi: Cơm chiên Dương Châu`) — 45,000 VND (~$1.80)
- **Broken Rice with Grilled Pork Chop (Cơm tấm sườn)** (`db_name_en: Broken Rice with Grilled Pork Chop` | `db_name_vi: Cơm tấm sườn`) — 50,000 VND (~$2.00)
- **Crab Noodle Soup (Bánh canh cua)** (`db_name_en: Crab noodle soup` | `db_name_vi: Bánh canh cua`) — 50,000 VND (~$2.00)
- **Hoi An Chicken Rice (Cơm gà Hội An)** (`db_name_en: Hoi An Chicken Rice` | `db_name_vi: Cơm gà Hội An`) — 50,000 VND (~$2.00)
- **Braised Pork with Eggs (Thịt kho tàu)** (`db_name_en: Braised Pork with Eggs` | `db_name_vi: Thịt kho tàu`) — 55,000 VND (~$2.20)
- **Braised Fish in Clay Pot (Cá kho tộ)** (`db_name_en: Braised fish in clay pot` | `db_name_vi: Cá kho tộ`) — 60,000 VND (~$2.40)
- **Sour Fish Soup (Canh chua cá hú)** (`db_name_en: Sour Fish Soup` | `db_name_vi: Canh chua cá hú`) — 60,000 VND (~$2.40)
- **Braised Catfish in Clay Pot (Cá hú kho tộ)** (`db_name_en: Braised Catfish in Clay Pot` | `db_name_vi: Cá hú kho tộ`) — 65,000 VND (~$2.60)

## Noodles / Mì

- **Beef Pho (Phở bò)** (`db_name_en: Beef Pho` | `db_name_vi: Phở bò`) — 45,000 VND (~$1.80)
- **Crab Tomato Vermicelli Soup (Bún riêu)** (`db_name_en: Crab Tomato Vermicelli Soup` | `db_name_vi: Bún riêu`) — 45,000 VND (~$1.80)
- **Quang Noodle (Mì Quảng)** (`db_name_en: Quang Noodle` | `db_name_vi: Mì Quảng`) — 45,000 VND (~$1.80)
- **Hanoi Grilled Pork with Vermicelli (Bún chả Hà Nội)** (`db_name_en: Hanoi Grilled Pork with Vermicelli` | `db_name_vi: Bún chả Hà Nội`) — 50,000 VND (~$2.00)
- **Hue Beef Noodle Soup (Bún bò Huế)** (`db_name_en: Hue Beef Noodle Soup` | `db_name_vi: Bún bò Huế`) — 50,000 VND (~$2.00)

## Grilled Dishes / Món nướnng

- **Grilled Chicken Feet (Chân gà nướng)** (`db_name_en: Grilled Chicken Feet` | `db_name_vi: Chân gà nướng`) — 45,000 VND (~$1.80)
- **Grilled Beef in Betel Leaves (Bò nướng lá lốt)** (`db_name_en: Grilled Beef in Betel Leaves` | `db_name_vi: Bò nướng lá lốt`) — 55,000 VND (~$2.20)
- **Grilled Chicken with Bamboo Rice (Gà nướng cơm lam)** (`db_name_en: Grilled Chicken with Bamboo Rice` | `db_name_vi: Gà nướng cơm lam`) — 70,000 VND (~$2.80)
- **BBQ Grilled Pork Ribs** (`db_name_en: BBQ Grilled Pork Ribs` | `db_name_vi: Sườn nướng BBQ`) — 75,000 VND (~$3.00)
- **BBQ Ribs** (`db_name_en: BBQ Ribs` | `db_name_vi: Sườn nướng BBQ`) — 100,000 VND (~$4.00)

## Seafood Dishes / Hải sản

- **Grilled Oysters with Scallion Oil (Hào nướng mỡ hành)** (`db_name_en: Grilled Oysters with Scallion Oil` | `db_name_vi: Hào nướng mỡ hành`) — 70,000 VND (~$2.80)
- **Thai-Style Steamed Clams (Nghêu hấp Thái)** (`db_name_en: Thai Style Steamed Clams` | `db_name_vi: Nghêu hấp Thái`) — 70,000 VND (~$2.80)
- **Grilled Shrimp with Chili Salt (Tôm nướng muối ớt)** (`db_name_en: Grilled Shrimp with Chili Salt` | `db_name_vi: Tôm nướng muối ớt`) — 75,000 VND (~$3.00)
- **Steamed Shrimp with Lemongrass (Tôm hấp sả)** (`db_name_en: Steamed Shrimp with Lemongrass` | `db_name_vi: Tôm hấp sả`) — 75,000 VND (~$3.00)
- **Grilled Squid with Satay (Mực nướng sa tế)** (`db_name_en: Grilled Squid with Satay` | `db_name_vi: Mực nướng sa tế`) — 80,000 VND (~$3.20)
- **Tamarind Fried Crab (Cua rang me)** (`db_name_en: Tamarind Fried Crab` | `db_name_vi: Cua rang me`) — 120,000 VND (~$4.80)

## Beverages / Đồ uống

- **Water (Nước lọc)** (`db_name_en: Water` | `db_name_vi: Nước lọc`) — 10,000 VND (~$0.40)
- **Pepsi (Pepsi)** (`db_name_en: Pepsi` | `db_name_vi: Pepsi`) — 15,000 VND (~$0.60)
- **Beer (Bia)** (`db_name_en: Beer` | `db_name_vi: Bia`) — 20,000 VND (~$0.80)
- **Orange Juice (Nước cam)** (`db_name_en: Orange Juice` | `db_name_vi: Nước cam`) — 25,000 VND (~$1.00)

## Hotpot / Lẩu

- **Chicken Hotpot with Basil (Lẩu gà lá é)** (`db_name_en: Chicken Hotpot with Basil` | `db_name_vi: Lẩu gà lá é`) — 180,000 VND (~$7.20)
- **Frog Hotpot (Lẩu ếch)** (`db_name_en: Frog Hotpot` | `db_name_vi: Lẩu ếch`) — 180,000 VND (~$7.20)
- **Crab Paste Hotpot (Lẩu riêu cua)** (`db_name_en: Crab Paste Hotpot` | `db_name_vi: Lẩu riêu cua`) — 190,000 VND (~$7.60)
- **Beef Hotpot (Lẩu bò)** (`db_name_en: Beef Hotpot` | `db_name_vi: Lẩu bò`) — 200,000 VND (~$8.00)
