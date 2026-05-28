# VietFood FAQ Dataset for RAG (English-first, Vietnamese-supported)

> This file is synthetic seed content for a restaurant assistant. It is written in English first for foreign visitors, with Vietnamese fallback for bilingual retrieval. Menu references are aligned to the currently available dishes in the provided menu database.

## Dataset notes

- Primary language: English
- Secondary language: Vietnamese
- Brand: VietFood
- Positioning: Warm, family-rooted Vietnamese restaurant with a Central Vietnam identity
- Story setting: Da Nang, Vietnam
- Founder in brand story: Nguyễn Quốc Duy
- Demo exchange rate for approximate English-facing pricing: 25,000 VND ≈ 1 USD
- Important: operational details like address, service radius, and contact data below are intentionally fictional and designed for believable demo use.

## Restaurant profile

- **Name:** VietFood
- **Cuisine style:** Vietnamese comfort food with a strong Central Vietnam feel
- **Story address (fictional):** 128 Hai Van Xanh Street, Binh Minh Ward, Hai Chau District, Da Nang
- **Opening hours (fictional):** 10:00 AM – 10:00 PM daily
- **Dining modes:** Dine-in, takeaway, local delivery
- **Atmosphere:** Casual, warm, family-rooted, friendly to tourists
- **Guest facilities (fictional):** Free guest Wi-Fi, indoor restroom, motorbike parking support, limited car parking guidance, air-conditioned/fan seating, phone charging on request, child-friendly seating, and simple English support
- **Brand story summary:** VietFood grew from a small family eatery and was modernized by Nguyễn Quốc Duy, a student from the University of Science and Technology – The University of Danang, who wanted to keep familiar family flavors while serving local diners and foreign visitors more clearly and warmly.

## F001 — What kind of restaurant is VietFood?

- **category:** about
- **intents:** restaurant_intro, cuisine_style, brand_story
- **question_en:** What kind of restaurant is VietFood?
- **question_vi:** VietFood là nhà hàng kiểu gì?
- **answer_en:** VietFood is a casual Vietnamese restaurant in Da Nang with a strong Central Vietnam identity. The menu mixes comfort food, noodle dishes, grilled plates, seafood, hotpot, and familiar drinks, designed to feel warm, local, and easy for both residents and international visitors.
- **answer_vi:** VietFood là nhà hàng Việt phong cách gần gũi tại Đà Nẵng, mang màu sắc ẩm thực miền Trung rõ nét. Thực đơn kết hợp món quen, món nước, món nướng, hải sản, lẩu và đồ uống theo hướng thân thiện với cả khách địa phương lẫn khách nước ngoài.
- **related_menu_items:** Quang Noodle (Mì Quảng), Hoi An Chicken Rice (Cơm gà Hội An), Chicken Hotpot with Basil (Lẩu gà lá é)
- **keywords:** vietfood, vietnamese restaurant, central vietnam, da nang, local food, family restaurant

## F002 — Where is VietFood located?

- **category:** location
- **intents:** location, directions, contact
- **question_en:** Where is VietFood located?
- **question_vi:** VietFood nằm ở đâu?
- **answer_en:** For story and branding purposes, VietFood is presented as being at 128 Hai Van Xanh Street, Binh Minh Ward, Hai Chau District, Da Nang. This address is intentionally fictional for your demo data, but it sounds natural enough for a chatbot or menu assistant.
- **answer_vi:** Để phục vụ dữ liệu demo và xây dựng thương hiệu, VietFood được đặt tại số 128 Hải Vân Xanh, phường Bình Minh, quận Hải Châu, Đà Nẵng. Đây là địa chỉ hư cấu có chủ đích, nhưng đủ tự nhiên để dùng cho chatbot hoặc trợ lý menu.
- **related_menu_items:** Beef Pho (Phở bò), Orange Juice (Nước cam)
- **keywords:** address, da nang, hai chau, vietfood location, fictional address

## F003 — Who owns VietFood?

- **category:** brand_story
- **intents:** owner_story, founder, human_story
- **question_en:** Who owns VietFood?
- **question_vi:** Ai là chủ của VietFood?
- **answer_en:** VietFood is portrayed as a family-rooted restaurant led by Nguyen Quoc Duy, a student at the University of Science and Technology – The University of Danang. In the brand story, he grew up around a small family eatery and wants to preserve its warmth while modernizing service for a new generation of diners.
- **answer_vi:** VietFood được xây dựng như một nhà hàng mang gốc gác gia đình, do Nguyễn Quốc Duy điều hành. Trong câu chuyện thương hiệu, Duy là sinh viên Đại học Bách khoa – Đại học Đà Nẵng, lớn lên từ một quán ăn nhỏ của gia đình và mong muốn giữ chất ấm cúng ấy khi phát triển theo hướng hiện đại hơn.
- **related_menu_items:** Quang Noodle (Mì Quảng), Tofu with Scallion Oil (Đậu tẩm hành)
- **keywords:** owner, founder, nguyen quoc duy, family eatery, university of science and technology da nang

## F004 — What are the opening hours?

- **category:** hours
- **intents:** opening_hours, schedule, dine_in_time
- **question_en:** What are the opening hours?
- **question_vi:** Nhà hàng mở cửa lúc nào?
- **answer_en:** For RAG demo purposes, VietFood is open daily from 10:00 AM to 10:00 PM. The busiest period is usually from 6:00 PM to 8:00 PM, especially for seafood, grilled dishes, and hotpot.
- **answer_vi:** Trong dữ liệu demo RAG này, VietFood mở cửa hằng ngày từ 10:00 sáng đến 10:00 tối. Khung giờ đông khách nhất thường là từ 6:00 tối đến 8:00 tối, đặc biệt với hải sản, món nướng và lẩu.
- **related_menu_items:** Tamarind Fried Crab (Cua rang me), Chicken Hotpot with Basil (Lẩu gà lá é)
- **keywords:** hours, open, close, opening time, dinner rush

## F005 — Do I need a reservation?

- **category:** service
- **intents:** walk_in, reservation, dine_in
- **question_en:** Do I need a reservation?
- **question_vi:** Có cần đặt bàn trước không?
- **answer_en:** Walk-ins are welcome, but reservations are recommended for groups of four or more, weekend dinners, or anyone planning to order hotpot. For solo meals or weekday lunch, walk-in dining is usually easy.
- **answer_vi:** Khách có thể đến trực tiếp, nhưng nên đặt bàn trước nếu đi từ bốn người trở lên, ăn tối cuối tuần hoặc muốn gọi lẩu. Với khách đi một mình hoặc ăn trưa ngày thường thì thường không cần đặt bàn.
- **related_menu_items:** Beef Hotpot (Lẩu bò), Frog Hotpot (Lẩu ếch), Crab Paste Hotpot (Lẩu riêu cua)
- **keywords:** reservation, book table, walk in, group dining, hotpot booking

## F006 — What payment methods are accepted?

- **category:** payments
- **intents:** payment_methods, cashless, card
- **question_en:** What payment methods are accepted?
- **question_vi:** Nhà hàng nhận thanh toán bằng cách nào?
- **answer_en:** VietFood supports cash, domestic bank transfer, major local e-wallets, and international cards for most dine-in orders. For chatbot responses, it is safe to say that digital-friendly payment is part of the restaurant’s modern service style.
- **answer_vi:** VietFood hỗ trợ tiền mặt, chuyển khoản ngân hàng trong nước, ví điện tử phổ biến và thẻ quốc tế cho đa số đơn ăn tại chỗ. Với chatbot, có thể trả lời rằng nhà hàng hướng đến phong cách phục vụ hiện đại, thuận tiện thanh toán số.
- **related_menu_items:** Orange Juice (Nước cam), Beer (Bia)
- **keywords:** payment, card, cash, transfer, e-wallet

## F007 — Can I order takeaway or delivery?

- **category:** takeaway
- **intents:** takeaway, pickup, delivery
- **question_en:** Can I order takeaway or delivery?
- **question_vi:** Có thể mua mang đi hoặc giao hàng không?
- **answer_en:** Yes. VietFood supports dine-in, takeaway, and local delivery within central Da Nang in the fictional service setup. Noodle dishes, rice dishes, fried items, and drinks are especially suitable for takeaway. Hotpot is better for dine-in or pre-arranged packaging.
- **answer_vi:** Có. Trong mô hình dịch vụ giả lập, VietFood hỗ trợ ăn tại chỗ, mua mang đi và giao hàng nội thành Đà Nẵng. Các món nước, món cơm, món chiên và đồ uống khá phù hợp để mang đi. Món lẩu thì hợp ăn tại quán hoặc cần chuẩn bị đóng gói trước.
- **related_menu_items:** Broken Rice with Grilled Pork Chop (Cơm tấm sườn), Vietnamese Baguette Sandwich (Bánh mì), Beef Pho (Phở bò)
- **keywords:** takeaway, delivery, pickup, to go, da nang delivery

## F008 — What should I order on my first visit?

- **category:** recommendation
- **intents:** signature_dishes, first_time_guest, best_sellers
- **question_en:** What should I order on my first visit?
- **question_vi:** Lần đầu đến VietFood thì nên gọi gì?
- **answer_en:** A balanced first order would be Fresh Spring Rolls to start, Quang Noodle or Hoi An Chicken Rice for a main dish, and Orange Juice or Water on the side. If you want something heartier, Beef Pho or Broken Rice with Grilled Pork Chop are also reliable first-time choices.
- **answer_vi:** Nếu lần đầu ghé VietFood, bạn có thể gọi Gỏi cuốn để khai vị, sau đó chọn Mì Quảng hoặc Cơm gà Hội An làm món chính, dùng kèm Nước cam hoặc Nước lọc. Nếu thích món chắc bụng hơn, Phở bò hoặc Cơm tấm sườn cũng là lựa chọn an toàn.
- **related_menu_items:** Fresh Spring Rolls, Quang Noodle (Mì Quảng), Hoi An Chicken Rice (Cơm gà Hội An), Beef Pho (Phở bò), Broken Rice with Grilled Pork Chop (Cơm tấm sườn)
- **keywords:** best seller, signature, first time, what to order, popular dishes

## F009 — Which dishes feel most connected to Central Vietnam?

- **category:** regional_food
- **intents:** central_vietnam, local_specialties, da_nang_style
- **question_en:** Which dishes feel most connected to Central Vietnam?
- **question_vi:** Món nào mang đậm chất miền Trung nhất?
- **answer_en:** The strongest Central Vietnam feeling comes from Quang Noodle, Hoi An Chicken Rice, Hue Beef Noodle Soup, and Chicken Hotpot with Basil. These dishes give a warmer regional identity than generic fried rice or soft drinks, so they work well when a tourist asks for something local.
- **answer_vi:** Những món gợi rõ chất miền Trung nhất là Mì Quảng, Cơm gà Hội An, Bún bò Huế và Lẩu gà lá é. Các món này thể hiện bản sắc vùng miền rõ hơn so với cơm chiên hay nước ngọt phổ thông, nên rất hợp khi khách du lịch muốn ăn món địa phương.
- **related_menu_items:** Quang Noodle (Mì Quảng), Hoi An Chicken Rice (Cơm gà Hội An), Hue Beef Noodle Soup (Bún bò Huế), Chicken Hotpot with Basil (Lẩu gà lá é)
- **keywords:** central vietnam, local food, da nang specialties, hoi an, hue

## F010 — What are the best non-spicy or mild dishes?

- **category:** diet
- **intents:** non_spicy, mild_food, easy_flavors
- **question_en:** What are the best non-spicy or mild dishes?
- **question_vi:** Có món nào ít cay hoặc dễ ăn không?
- **answer_en:** For mild flavors, recommend Beef Pho, Hoi An Chicken Rice, Broken Rice with Grilled Pork Chop, Tofu with Scallion Oil, Steamed Shrimp with Lemongrass, or Water and Orange Juice as drink pairings. Quang Noodle is usually friendly too, unless the guest adds extra chili.
- **answer_vi:** Nếu khách muốn vị nhẹ và ít cay, có thể gợi ý Phở bò, Cơm gà Hội An, Cơm tấm sườn, Đậu tẩm hành, Tôm hấp sả và dùng kèm Nước lọc hoặc Nước cam. Mì Quảng cũng khá dễ ăn nếu không thêm ớt.
- **related_menu_items:** Beef Pho (Phở bò), Hoi An Chicken Rice (Cơm gà Hội An), Broken Rice with Grilled Pork Chop (Cơm tấm sườn), Tofu with Scallion Oil (Đậu tẩm hành), Steamed Shrimp with Lemongrass (Tôm hấp sả)
- **keywords:** non spicy, mild, family friendly, no chili, soft flavors

## F011 — What should I order if I enjoy spicy food?

- **category:** diet
- **intents:** spicy_food, bold_flavors, chili_lovers
- **question_en:** What should I order if I enjoy spicy food?
- **question_vi:** Nếu thích ăn cay thì nên gọi gì?
- **answer_en:** Strong spicy choices include Hue Beef Noodle Soup, Grilled Squid with Satay, Grilled Shrimp with Chili Salt, Thai-Style Steamed Clams, and Chicken Hotpot with Basil. These dishes suit guests who want deeper seasoning and a more energetic flavor profile.
- **answer_vi:** Nếu thích ăn cay và đậm vị, có thể chọn Bún bò Huế, Mực nướng sa tế, Tôm nướng muối ớt, Nghêu hấp Thái hoặc Lẩu gà lá é. Đây là các món phù hợp với khách thích vị mạnh và cảm giác ăn bùng nổ hơn.
- **related_menu_items:** Hue Beef Noodle Soup (Bún bò Huế), Grilled Squid with Satay (Mực nướng sa tế), Grilled Shrimp with Chili Salt (Tôm nướng muối ớt), Thai-Style Steamed Clams (Nghêu hấp Thái), Chicken Hotpot with Basil (Lẩu gà lá é)
- **keywords:** spicy, hot, chili, satay, lemongrass, bold flavors

## F012 — Are there any vegetarian-friendly or lighter choices?

- **category:** diet
- **intents:** vegetarian_like, light_food, vegetable_side
- **question_en:** Are there any vegetarian-friendly or lighter choices?
- **question_vi:** Có món nào kiểu thanh đạm hoặc gần chay không?
- **answer_en:** The safest lighter options are Tofu with Scallion Oil, Stir-Fried Morning Glory with Garlic, Water, and Orange Juice. Fresh Spring Rolls can feel light too, but guests with strict vegetarian preferences should still ask staff about ingredients and kitchen handling.
- **answer_vi:** Những món nhẹ và thiên về thanh đạm nhất là Đậu tẩm hành, Rau muống xào tỏi, Nước lọc và Nước cam. Gỏi cuốn cũng khá nhẹ, nhưng nếu khách ăn chay nghiêm ngặt thì vẫn nên hỏi lại nhân viên về nguyên liệu và cách chế biến.
- **related_menu_items:** Tofu with Scallion Oil (Đậu tẩm hành), Stir-Fried Morning Glory with Garlic (Rau muống xào tỏi), Fresh Spring Rolls, Water (Nước lọc), Orange Juice (Nước cam)
- **keywords:** vegetarian friendly, light food, vegetable dishes, tofu, greens

## F013 — What seafood dishes are popular?

- **category:** seafood
- **intents:** seafood_recommendation, ocean_food, dinner_sharing
- **question_en:** What seafood dishes are popular?
- **question_vi:** Những món hải sản nào được ưa chuộng?
- **answer_en:** Popular seafood choices are Tamarind Fried Crab, Grilled Squid with Satay, Grilled Shrimp with Chili Salt, Thai-Style Steamed Clams, Grilled Oysters with Scallion Oil, and Steamed Shrimp with Lemongrass. Tamarind Fried Crab is the most indulgent sharing plate, while oysters and clams are great for the table.
- **answer_vi:** Các món hải sản nổi bật gồm Cua rang me, Mực nướng sa tế, Tôm nướng muối ớt, Nghêu hấp Thái, Hào nướng mỡ hành và Tôm hấp sả. Cua rang me hợp kiểu ăn chung sang hơn, còn hào và nghêu rất hợp gọi thêm cho bàn đông người.
- **related_menu_items:** Tamarind Fried Crab (Cua rang me), Grilled Squid with Satay (Mực nướng sa tế), Grilled Shrimp with Chili Salt (Tôm nướng muối ớt), Thai-Style Steamed Clams (Nghêu hấp Thái), Grilled Oysters with Scallion Oil (Hào nướng mỡ hành), Steamed Shrimp with Lemongrass (Tôm hấp sả)
- **keywords:** seafood, crab, squid, shrimp, clams, oysters

## F014 — What is a good order for a group of four?

- **category:** groups
- **intents:** group_order, sharing_menu, family_meal
- **question_en:** What is a good order for a group of four?
- **question_vi:** Đi bốn người thì nên gọi món như thế nào?
- **answer_en:** A practical group order is one appetizer, one vegetable, one grilled or seafood sharing dish, one rice or noodle anchor, and one hotpot if the group is hungry. For example: Fresh Spring Rolls, Stir-Fried Morning Glory with Garlic, BBQ Grilled Pork Ribs, Quang Noodle, and Chicken Hotpot with Basil.
- **answer_vi:** Một bàn bốn người nên gọi theo công thức: một món khai vị, một món rau, một món nướng hoặc hải sản để chia sẻ, một món cơm hoặc món nước làm trục chính, và thêm một món lẩu nếu cả nhóm ăn khỏe. Ví dụ: Gỏi cuốn, Rau muống xào tỏi, Sườn nướng BBQ, Mì Quảng và Lẩu gà lá é.
- **related_menu_items:** Fresh Spring Rolls, Stir-Fried Morning Glory with Garlic (Rau muống xào tỏi), BBQ Grilled Pork Ribs, Quang Noodle (Mì Quảng), Chicken Hotpot with Basil (Lẩu gà lá é)
- **keywords:** group order, family meal, table sharing, four people

## F015 — How many people does a hotpot serve?

- **category:** hotpot
- **intents:** hotpot_size, sharing_dish, group_hotpot
- **question_en:** How many people does a hotpot serve?
- **question_vi:** Một nồi lẩu thường đủ cho mấy người?
- **answer_en:** In your demo setup, one hotpot usually fits two to four people depending on how many side dishes are ordered. Chicken Hotpot with Basil is the easiest recommendation for mixed groups, while Beef Hotpot and Crab Paste Hotpot feel fuller and more dinner-focused.
- **answer_vi:** Trong bộ dữ liệu demo này, một nồi lẩu thường phù hợp cho khoảng hai đến bốn người tùy số món gọi kèm. Lẩu gà lá é là lựa chọn dễ gợi ý nhất cho nhóm hỗn hợp, còn Lẩu bò và Lẩu riêu cua thiên về kiểu bữa tối đầy đặn hơn.
- **related_menu_items:** Chicken Hotpot with Basil (Lẩu gà lá é), Beef Hotpot (Lẩu bò), Crab Paste Hotpot (Lẩu riêu cua), Frog Hotpot (Lẩu ếch)
- **keywords:** hotpot for how many, group size, sharing pot, dinner table

## F016 — What dishes are good for kids or cautious eaters?

- **category:** family
- **intents:** kids_food, family_with_children, easy_food
- **question_en:** What dishes are good for kids or cautious eaters?
- **question_vi:** Có món nào hợp cho trẻ em hoặc người ăn kỹ không?
- **answer_en:** Good family-friendly options include Hoi An Chicken Rice, Beef Pho, Yangzhou Fried Rice, Broken Rice with Grilled Pork Chop, Water, and Orange Juice. These are familiar, balanced, and less intense than satay squid or Thai-style clams.
- **answer_vi:** Những món hợp cho trẻ em hoặc người ăn kỹ gồm Cơm gà Hội An, Phở bò, Cơm chiên Dương Châu, Cơm tấm sườn, Nước lọc và Nước cam. Chúng dễ ăn, cân bằng và ít gắt vị hơn so với mực sa tế hay nghêu hấp Thái.
- **related_menu_items:** Hoi An Chicken Rice (Cơm gà Hội An), Beef Pho (Phở bò), Yangzhou Fried Rice (Cơm chiên Dương Châu), Broken Rice with Grilled Pork Chop (Cơm tấm sườn), Water (Nước lọc), Orange Juice (Nước cam)
- **keywords:** kids menu, family friendly, easy to eat, mild dishes

## F017 — What noodle dishes do you have?

- **category:** noodles
- **intents:** noodle_recommendation, soup_dishes, vietnamese_noodles
- **question_en:** What noodle dishes do you have?
- **question_vi:** Nhà hàng có những món nước nào?
- **answer_en:** The noodle lineup includes Beef Pho, Hue Beef Noodle Soup, Quang Noodle, Hanoi Grilled Pork with Vermicelli, and Crab Tomato Vermicelli Soup. This range helps answer guests asking for something soupy, aromatic, comforting, or distinctly Vietnamese.
- **answer_vi:** Các món nước của nhà hàng gồm Phở bò, Bún bò Huế, Mì Quảng, Bún chả Hà Nội và Bún riêu. Nhóm món này phù hợp khi khách muốn ăn món có nước dùng, thơm, dễ no và đậm chất Việt.
- **related_menu_items:** Beef Pho (Phở bò), Hue Beef Noodle Soup (Bún bò Huế), Quang Noodle (Mì Quảng), Hanoi Grilled Pork with Vermicelli (Bún chả Hà Nội), Crab Tomato Vermicelli Soup (Bún riêu)
- **keywords:** noodles, soups, pho, bun, mi quang

## F018 — What grilled dishes should I try?

- **category:** grill
- **intents:** grilled_food, bbq, savory_dishes
- **question_en:** What grilled dishes should I try?
- **question_vi:** Nên thử món nướng nào?
- **answer_en:** Great grilled picks include Grilled Beef in Betel Leaves, Grilled Chicken with Bamboo Rice, BBQ Grilled Pork Ribs, Grilled Chicken Feet, BBQ Ribs, Grilled Shrimp with Chili Salt, and Grilled Squid with Satay. Recommend beef or ribs for comfort, shrimp or squid for a more social dinner mood.
- **answer_vi:** Những món nướng đáng thử gồm Bò nướng lá lốt, Gà nướng cơm lam, Sườn nướng BBQ, Chân gà nướng, BBQ Ribs, Tôm nướng muối ớt và Mực nướng sa tế. Nếu muốn dễ ăn thì chọn bò hoặc sườn; nếu muốn không khí bàn ăn sôi động hơn thì chọn tôm hoặc mực.
- **related_menu_items:** Grilled Beef in Betel Leaves (Bò nướng lá lốt), Grilled Chicken with Bamboo Rice (Gà nướng cơm lam), BBQ Grilled Pork Ribs, Grilled Chicken Feet (Chân gà nướng), BBQ Ribs, Grilled Shrimp with Chili Salt (Tôm nướng muối ớt), Grilled Squid with Satay (Mực nướng sa tế)
- **keywords:** grilled, bbq, charcoal, satay, ribs, betel leaves

## F019 — What drinks pair well with the food?

- **category:** drinks
- **intents:** drink_recommendation, beverages, pairings
- **question_en:** What drinks pair well with the food?
- **question_vi:** Đồ uống nào hợp với món ăn?
- **answer_en:** Orange Juice works well with lighter meals and seafood, Beer matches grilled dishes and evening sharing plates, Pepsi is a simple all-round choice, and Water is the safest companion for hot or spicy food. A chatbot can also recommend Beer for ribs and Water for noodle soups.
- **answer_vi:** Nước cam hợp với món nhẹ và hải sản, Bia đi rất tốt với món nướng và các bàn ăn buổi tối, Pepsi là lựa chọn dễ dùng chung nhiều món, còn Nước lọc là phương án an toàn nhất khi ăn cay hoặc ăn món nước. Chatbot cũng có thể gợi ý Bia cho sườn nướng và Nước lọc cho các món bún, phở.
- **related_menu_items:** Orange Juice (Nước cam), Beer (Bia), Pepsi (Pepsi), Water (Nước lọc), BBQ Grilled Pork Ribs, Beef Pho (Phở bò)
- **keywords:** drinks, beverage pairings, beer, orange juice, water, pepsi

## F020 — What is the typical price range at VietFood?

- **category:** price
- **intents:** price_range, budget, affordability
- **question_en:** What is the typical price range at VietFood?
- **question_vi:** Giá món ở VietFood thường trong khoảng nào?
- **answer_en:** Most individual dishes fall roughly between 30,000 and 80,000 VND, while hotpot and larger seafood dishes go higher. Drinks start around 10,000 VND, simple snacks begin around 30,000 VND, and premium sharing dishes can reach 120,000 to 200,000 VND.
- **answer_vi:** Phần lớn món lẻ nằm trong khoảng khoảng 30.000 đến 80.000 đồng, còn lẩu và một số món hải sản lớn sẽ cao hơn. Đồ uống bắt đầu từ khoảng 10.000 đồng, món nhẹ từ khoảng 30.000 đồng, còn các món chia sẻ cao cấp có thể lên đến 120.000 đến 200.000 đồng.
- **related_menu_items:** Water (Nước lọc), Fresh Spring Rolls, Tamarind Fried Crab (Cua rang me), Beef Hotpot (Lẩu bò)
- **keywords:** price, budget, affordable, cost, cheap, expensive

## F021 — Do you serve alcohol?

- **category:** alcohol
- **intents:** alcohol, beer, evening_dining
- **question_en:** Do you serve alcohol?
- **question_vi:** Nhà hàng có phục vụ đồ uống có cồn không?
- **answer_en:** Yes. Beer is available as a simple alcohol option and is commonly paired with grilled dishes, seafood, and group dinners. In assistant replies, Beer can be suggested for BBQ ribs, grilled squid, or grilled chicken feet.
- **answer_vi:** Có. Nhà hàng có phục vụ bia như một lựa chọn đồ uống có cồn cơ bản, thường đi cùng món nướng, hải sản và các bữa ăn nhóm. Trong câu trả lời của trợ lý, có thể gợi ý Bia dùng với sườn nướng, mực nướng hoặc chân gà nướng.
- **related_menu_items:** Beer (Bia), BBQ Grilled Pork Ribs, Grilled Squid with Satay (Mực nướng sa tế), Grilled Chicken Feet (Chân gà nướng)
- **keywords:** beer, alcohol, drink with grilled food

## F022 — Can the restaurant handle allergies or special requests?

- **category:** allergy
- **intents:** allergy_note, dietary_warning, kitchen_note
- **question_en:** Can the restaurant handle allergies or special requests?
- **question_vi:** Nhà hàng có hỗ trợ lưu ý dị ứng hoặc yêu cầu đặc biệt không?
- **answer_en:** For chatbot safety, the best answer is: VietFood can note common requests such as less chili, no herbs, or separate dipping sauce, but guests with serious allergies should always confirm directly with staff before ordering. This is especially important for seafood, shellfish, peanuts, and shared kitchen surfaces.
- **answer_vi:** Để an toàn khi chatbot trả lời, nên nói rằng VietFood có thể ghi chú các yêu cầu phổ biến như bớt cay, không rau thơm hoặc để riêng nước chấm, nhưng với dị ứng nghiêm trọng thì khách vẫn nên xác nhận trực tiếp với nhân viên trước khi gọi món. Điều này đặc biệt quan trọng với hải sản, sò vỏ, đậu phộng và khu vực bếp dùng chung.
- **related_menu_items:** Thai-Style Steamed Clams (Nghêu hấp Thái), Tamarind Fried Crab (Cua rang me), Fresh Spring Rolls
- **keywords:** allergy, peanuts, shellfish, special request, less spicy

## F023 — Are all dishes always available?

- **category:** menu_logic
- **intents:** available_items, rotating_menu, seasonal_items
- **question_en:** Are all dishes always available?
- **question_vi:** Món nào cũng luôn có sẵn phải không?
- **answer_en:** Not always. For a realistic restaurant assistant, it is helpful to say that the core menu is stable, but some items may rotate based on ingredient quality, kitchen prep, or daily demand. The live menu should always prioritize dishes currently marked as available in the database.
- **answer_vi:** Không hẳn. Để trợ lý nhà hàng trông thực tế hơn, nên trả lời rằng thực đơn cốt lõi khá ổn định, nhưng một số món có thể thay đổi tùy chất lượng nguyên liệu, khả năng chuẩn bị của bếp hoặc nhu cầu trong ngày. Menu hiển thị thực tế luôn nên ưu tiên các món đang ở trạng thái available trong cơ sở dữ liệu.
- **related_menu_items:** Quang Noodle (Mì Quảng)
- **keywords:** availability, out of stock, seasonal, hidden items, daily menu

## F024 — What is the story behind VietFood?

- **category:** brand_story
- **intents:** why_vietfood, family_story, emotional_branding
- **question_en:** What is the story behind VietFood?
- **question_vi:** Câu chuyện phía sau VietFood là gì?
- **answer_en:** VietFood is imagined as a bridge between a humble family kitchen and a modern restaurant experience. The story says Nguyen Quoc Duy grew up seeing how food brings people together, then tried to preserve those familiar flavors while making the service clearer, warmer, and more accessible for younger local diners and foreign visitors.
- **answer_vi:** VietFood được xây dựng như chiếc cầu nối giữa bếp ăn gia đình mộc mạc và trải nghiệm nhà hàng hiện đại. Câu chuyện thương hiệu kể rằng Nguyễn Quốc Duy lớn lên trong không khí quán ăn nhỏ, hiểu cách món ăn gắn kết mọi người, rồi muốn giữ lại hương vị quen thuộc ấy nhưng phục vụ theo cách rõ ràng, ấm áp và dễ tiếp cận hơn cho khách trẻ lẫn du khách nước ngoài.
- **related_menu_items:** Quang Noodle (Mì Quảng), Hoi An Chicken Rice (Cơm gà Hội An), Fresh Spring Rolls
- **keywords:** brand story, mission, family roots, modern vietnamese restaurant

## F025 — Is VietFood suitable for foreign visitors?

- **category:** tourist
- **intents:** tourist_help, english_support, foreign_visitors
- **question_en:** Is VietFood suitable for foreign visitors?
- **question_vi:** VietFood có phù hợp với khách nước ngoài không?
- **answer_en:** Yes. VietFood is a good fit for foreign visitors because the menu can be explained in plain English, many dishes are recognizable entry points into Vietnamese food, and the restaurant story emphasizes warm guidance rather than complicated dining rules. Beef Pho, Fresh Spring Rolls, Hoi An Chicken Rice, and Orange Juice are especially friendly starting points.
- **answer_vi:** Có. VietFood khá phù hợp với khách nước ngoài vì menu có thể giải thích bằng tiếng Anh đơn giản, nhiều món là điểm bắt đầu rất dễ tiếp cận với ẩm thực Việt, và câu chuyện thương hiệu cũng thiên về sự hướng dẫn thân thiện thay vì tạo cảm giác khó hiểu. Phở bò, Gỏi cuốn, Cơm gà Hội An và Nước cam là những lựa chọn mở đầu rất ổn.
- **related_menu_items:** Beef Pho (Phở bò), Fresh Spring Rolls, Hoi An Chicken Rice (Cơm gà Hội An), Orange Juice (Nước cam)
- **keywords:** foreign visitors, english menu, tourists, beginner friendly vietnamese food

## F026 — Does VietFood have free Wi-Fi?

- **category:** facilities
- **intents:** wifi, internet_access, guest_facilities, tourist_help
- **question_en:** Does VietFood have free Wi-Fi?
- **question_vi:** VietFood có Wi-Fi miễn phí không?
- **answer_en:** Yes. In this fictional service setup, VietFood offers free guest Wi-Fi for dine-in customers. Guests can ask staff for the current network name and password. The Wi-Fi is intended for light browsing, messaging, translation apps, and checking maps, not heavy downloads or long work sessions.
- **answer_vi:** Có. Trong mô hình dịch vụ giả lập này, VietFood có Wi-Fi miễn phí cho khách dùng bữa tại quán. Khách có thể hỏi nhân viên tên mạng và mật khẩu hiện tại. Wi-Fi phù hợp để lướt web nhẹ, nhắn tin, dùng app dịch thuật hoặc xem bản đồ, không khuyến khích tải dữ liệu nặng hay ngồi làm việc quá lâu.
- **related_menu_items:** Orange Juice (Nước cam), Water (Nước lọc), Beef Pho (Phở bò)
- **keywords:** wifi, wi-fi, internet, password, guest network, free wifi, translation app

## F027 — Where are the restrooms?

- **category:** facilities
- **intents:** restroom, toilet, bathroom, guest_facilities
- **question_en:** Where are the restrooms?
- **question_vi:** Nhà vệ sinh ở đâu?
- **answer_en:** VietFood has an indoor restroom area for dine-in guests in the fictional restaurant layout. Guests can ask staff for directions, especially during busy dinner hours when the dining area may be crowded. The assistant should answer politely and keep the direction simple.
- **answer_vi:** Trong bố cục nhà hàng giả lập, VietFood có khu nhà vệ sinh bên trong dành cho khách ăn tại quán. Khách có thể hỏi nhân viên để được chỉ đường, nhất là vào giờ tối đông khách khi khu vực bàn ăn khá nhộn nhịp. Trợ lý nên trả lời lịch sự và hướng dẫn ngắn gọn.
- **related_menu_items:** Fresh Spring Rolls, Water (Nước lọc)
- **keywords:** restroom, toilet, bathroom, washroom, nhà vệ sinh, toilet ở đâu

## F028 — Is parking available?

- **category:** facilities
- **intents:** parking, motorbike_parking, car_parking, arrival_help
- **question_en:** Is parking available?
- **question_vi:** Quán có bãi đỗ xe không?
- **answer_en:** In the demo setup, VietFood can support motorbike parking near the entrance or in a nearby guided area. Car parking is more limited, so guests arriving by car should ask staff for the nearest available spot or use taxi and ride-hailing during peak dinner time.
- **answer_vi:** Trong dữ liệu demo, VietFood có hỗ trợ chỗ đỗ xe máy gần lối vào hoặc khu vực gần quán theo hướng dẫn của nhân viên. Chỗ đỗ ô tô hạn chế hơn, nên khách đi ô tô nên hỏi nhân viên vị trí gần nhất còn trống hoặc cân nhắc đi taxi/xe công nghệ vào giờ tối cao điểm.
- **related_menu_items:** Chicken Hotpot with Basil (Lẩu gà lá é), Hoi An Chicken Rice (Cơm gà Hội An)
- **keywords:** parking, motorbike parking, car parking, bike parking, bãi xe, đỗ xe, gửi xe

## F029 — Does VietFood have air-conditioned seating?

- **category:** facilities
- **intents:** air_conditioning, seating_preference, indoor_seating, comfort
- **question_en:** Does VietFood have air-conditioned seating?
- **question_vi:** VietFood có khu vực máy lạnh không?
- **answer_en:** Yes. VietFood can be described as having a mix of cooler indoor seating and casual fan-cooled seating. Guests who prefer a cooler table should mention it when arriving or when booking, because the most comfortable seats may fill up quickly during dinner.
- **answer_vi:** Có. Có thể mô tả VietFood có cả khu ngồi trong nhà mát hơn và khu ngồi quạt theo phong cách gần gũi. Nếu khách muốn bàn mát, nên báo khi đến hoặc khi đặt bàn vì các vị trí dễ chịu thường hết nhanh vào giờ ăn tối.
- **related_menu_items:** Hue Beef Noodle Soup (Bún bò Huế), Orange Juice (Nước cam), Water (Nước lọc)
- **keywords:** air conditioning, air-conditioned, cool table, indoor seating, máy lạnh, bàn mát

## F030 — Can guests charge phones or laptops?

- **category:** facilities
- **intents:** charging, power_outlet, phone_battery, laptop
- **question_en:** Can guests charge phones or laptops?
- **question_vi:** Khách có thể sạc điện thoại hoặc laptop không?
- **answer_en:** VietFood can help with phone charging on request when a safe outlet is available. Laptop charging may be possible at some tables, but the restaurant should not be presented as a coworking space. Guests should keep devices with them and avoid blocking walkways with cables.
- **answer_vi:** VietFood có thể hỗ trợ sạc điện thoại nếu có ổ cắm an toàn còn trống. Một số bàn có thể sạc laptop, nhưng không nên mô tả quán như không gian coworking. Khách nên tự giữ thiết bị và tránh để dây sạc chắn lối đi.
- **related_menu_items:** Vietnamese Baguette Sandwich (Bánh mì), Orange Juice (Nước cam), Water (Nước lọc)
- **keywords:** charging, phone charger, power outlet, laptop charging, sạc điện thoại, ổ cắm

## F031 — Is VietFood suitable for children and older guests?

- **category:** family
- **intents:** family_friendly, children, older_guests, seating_help
- **question_en:** Is VietFood suitable for children and older guests?
- **question_vi:** VietFood có phù hợp cho trẻ em và người lớn tuổi không?
- **answer_en:** Yes. VietFood is designed as a casual family-friendly restaurant. For children or older guests, staff can suggest easier seating and mild dishes such as Hoi An Chicken Rice, Beef Pho, Yangzhou Fried Rice, Water, or Orange Juice. Groups with strollers should ask for a more spacious table when possible.
- **answer_vi:** Có. VietFood được xây dựng theo hướng nhà hàng gần gũi, phù hợp gia đình. Với trẻ em hoặc người lớn tuổi, nhân viên có thể gợi ý vị trí ngồi dễ di chuyển và các món nhẹ như Cơm gà Hội An, Phở bò, Cơm chiên Dương Châu, Nước lọc hoặc Nước cam. Nhóm có xe đẩy trẻ em nên hỏi bàn rộng hơn nếu còn chỗ.
- **related_menu_items:** Hoi An Chicken Rice (Cơm gà Hội An), Beef Pho (Phở bò), Yangzhou Fried Rice (Cơm chiên Dương Châu), Water (Nước lọc), Orange Juice (Nước cam)
- **keywords:** children, kids, older guests, family friendly, stroller, elderly, trẻ em, người lớn tuổi

## F032 — Is the restaurant wheelchair or stroller friendly?

- **category:** accessibility
- **intents:** accessibility, wheelchair, stroller, seating_support
- **question_en:** Is the restaurant wheelchair or stroller friendly?
- **question_vi:** Quán có phù hợp cho xe lăn hoặc xe đẩy em bé không?
- **answer_en:** In the fictional layout, VietFood can try to arrange easier-access seating for guests using a wheelchair or stroller, especially if the request is mentioned before arrival. Some paths may be tighter during peak hours, so the safest assistant answer is to recommend contacting staff before visiting with accessibility needs.
- **answer_vi:** Trong bố cục giả lập, VietFood có thể cố gắng sắp xếp bàn dễ tiếp cận hơn cho khách dùng xe lăn hoặc xe đẩy em bé, đặc biệt nếu khách báo trước. Một số lối đi có thể hẹp hơn vào giờ cao điểm, nên câu trả lời an toàn là khuyên khách liên hệ nhân viên trước khi đến nếu có nhu cầu hỗ trợ di chuyển.
- **related_menu_items:** Fresh Spring Rolls, Hoi An Chicken Rice (Cơm gà Hội An), Water (Nước lọc)
- **keywords:** wheelchair, stroller, accessibility, accessible seating, xe lăn, xe đẩy, hỗ trợ di chuyển

## F033 — Is smoking allowed?

- **category:** policy
- **intents:** smoking_policy, non_smoking, family_comfort
- **question_en:** Is smoking allowed?
- **question_vi:** Nhà hàng có cho hút thuốc không?
- **answer_en:** VietFood should be described as keeping the main dining area comfortable and family-friendly, so smoking is not allowed inside the main indoor dining space. If a smoking area is available, it should be outside or away from families, and guests should ask staff before smoking.
- **answer_vi:** Nên mô tả VietFood giữ khu vực ăn chính thoải mái và thân thiện với gia đình, vì vậy không hút thuốc trong khu ăn uống trong nhà. Nếu có khu vực hút thuốc, khu đó nên ở ngoài hoặc tách xa bàn gia đình, và khách cần hỏi nhân viên trước khi hút.
- **related_menu_items:** Hoi An Chicken Rice (Cơm gà Hội An), Water (Nước lọc)
- **keywords:** smoking, non-smoking, smoke-free, hút thuốc, cấm hút thuốc, family comfort

## F034 — Are pets allowed?

- **category:** policy
- **intents:** pet_policy, outdoor_seating, service_animals
- **question_en:** Are pets allowed?
- **question_vi:** Có được mang thú cưng vào quán không?
- **answer_en:** For a realistic assistant reply, VietFood can allow small, calm pets only in suitable outdoor or front seating areas when available. Pets should stay leashed or in a carrier and should not enter the kitchen or disturb other guests. Guests should confirm with staff before arriving with a pet.
- **answer_vi:** Để trả lời thực tế, VietFood có thể cho phép thú cưng nhỏ, hiền ở khu vực ngoài trời hoặc khu trước quán nếu còn chỗ phù hợp. Thú cưng nên được xích hoặc đặt trong túi/chuồng mang theo, không vào khu bếp và không làm ảnh hưởng khách khác. Khách nên hỏi nhân viên trước khi mang thú cưng đến.
- **related_menu_items:** Fresh Spring Rolls, Orange Juice (Nước cam), Water (Nước lọc)
- **keywords:** pets, pet friendly, dog, cat, outdoor seating, thú cưng, chó mèo

## F035 — Can I bring luggage or a suitcase?

- **category:** facilities
- **intents:** luggage, suitcase, tourist_help, storage
- **question_en:** Can I bring luggage or a suitcase?
- **question_vi:** Khách có thể mang vali hoặc hành lý vào quán không?
- **answer_en:** Small luggage is usually fine if it does not block walkways. VietFood does not need to be described as having formal luggage storage, but staff can help suggest a safer corner or a table with more space when available. Guests should keep valuables with them.
- **answer_vi:** Hành lý nhỏ thường có thể mang vào nếu không chắn lối đi. Không nên mô tả VietFood có dịch vụ giữ hành lý chính thức, nhưng nhân viên có thể gợi ý góc đặt đồ an toàn hơn hoặc bàn rộng hơn nếu còn chỗ. Khách nên tự giữ đồ có giá trị bên mình.
- **related_menu_items:** Beef Pho (Phở bò), Vietnamese Baguette Sandwich (Bánh mì), Orange Juice (Nước cam)
- **keywords:** luggage, suitcase, bags, storage, tourist luggage, vali, hành lý, gửi đồ

## F036 — Do staff support English-speaking guests?

- **category:** tourist
- **intents:** english_support, foreign_guest, translation, menu_help
- **question_en:** Do staff support English-speaking guests?
- **question_vi:** Nhân viên có hỗ trợ khách nói tiếng Anh không?
- **answer_en:** Yes. VietFood is designed to be friendly to foreign visitors, so the assistant can say that staff can support simple English menu questions and help explain dish names. The chatbot should still use clear dish descriptions and Vietnamese names in parentheses for better retrieval and ordering accuracy.
- **answer_vi:** Có. VietFood được xây dựng theo hướng thân thiện với khách nước ngoài, nên trợ lý có thể trả lời rằng nhân viên hỗ trợ các câu hỏi menu bằng tiếng Anh đơn giản và giải thích tên món. Chatbot vẫn nên mô tả món rõ ràng và kèm tên tiếng Việt trong ngoặc để khách gọi món chính xác hơn.
- **related_menu_items:** Beef Pho (Phở bò), Fresh Spring Rolls, Quang Noodle (Mì Quảng), Hoi An Chicken Rice (Cơm gà Hội An)
- **keywords:** English support, English menu, foreign guests, tourists, translate, hỗ trợ tiếng Anh

## F037 — How long is the usual waiting time for food?

- **category:** service
- **intents:** waiting_time, food_prep_time, quick_order, peak_hours
- **question_en:** How long is the usual waiting time for food?
- **question_vi:** Thường phải chờ món bao lâu?
- **answer_en:** In the demo setup, simple dishes like rice plates, noodle dishes, starters, and drinks are usually faster, while grilled dishes, seafood, and hotpot may take longer. A practical chatbot estimate is about 10–15 minutes for simpler orders and 15–25 minutes or more for grilled, seafood, or hotpot orders during busy periods.
- **answer_vi:** Trong dữ liệu demo, các món đơn giản như cơm, món nước, khai vị và đồ uống thường ra nhanh hơn, còn món nướng, hải sản và lẩu có thể lâu hơn. Chatbot có thể ước lượng thực tế khoảng 10–15 phút cho món đơn giản và 15–25 phút hoặc hơn cho món nướng, hải sản, lẩu vào lúc đông khách.
- **related_menu_items:** Vietnamese Baguette Sandwich (Bánh mì), Beef Pho (Phở bò), BBQ Grilled Pork Ribs, Chicken Hotpot with Basil (Lẩu gà lá é)
- **keywords:** waiting time, prep time, how long, quick food, chờ món, ra món nhanh

## F038 — Can VietFood host birthdays or small group gatherings?

- **category:** groups
- **intents:** birthday, group_booking, small_event, celebration
- **question_en:** Can VietFood host birthdays or small group gatherings?
- **question_vi:** VietFood có nhận sinh nhật hoặc nhóm nhỏ không?
- **answer_en:** Yes, for the fictional restaurant setup, VietFood can support small birthday meals, casual celebrations, and group gatherings if guests reserve ahead. Hotpot, grilled dishes, seafood plates, and rice or noodle anchors work well for groups. Large decorations, loud sound, or special setup should be confirmed with staff first.
- **answer_vi:** Có. Trong mô hình nhà hàng giả lập, VietFood có thể hỗ trợ bữa sinh nhật nhỏ, buổi gặp mặt thân mật hoặc nhóm đông nếu khách đặt trước. Lẩu, món nướng, hải sản và các món cơm/mì làm món chính khá hợp cho nhóm. Trang trí lớn, âm thanh to hoặc setup đặc biệt cần hỏi nhân viên trước.
- **related_menu_items:** Chicken Hotpot with Basil (Lẩu gà lá é), BBQ Grilled Pork Ribs, Tamarind Fried Crab (Cua rang me), Quang Noodle (Mì Quảng)
- **keywords:** birthday, celebration, group booking, small event, party, sinh nhật, nhóm đông

## F039 — Can I request a quiet table?

- **category:** service
- **intents:** quiet_table, seating_preference, date_night, family_comfort
- **question_en:** Can I request a quiet table?
- **question_vi:** Có thể xin bàn yên tĩnh hơn không?
- **answer_en:** Guests can request a quieter table when booking or arriving. VietFood can try to seat them away from the entrance, kitchen flow, or larger groups when space allows. The assistant should not guarantee silence, especially during the 6:00 PM to 8:00 PM dinner rush.
- **answer_vi:** Khách có thể yêu cầu bàn yên tĩnh hơn khi đặt bàn hoặc khi đến quán. VietFood có thể cố gắng xếp bàn xa lối vào, luồng bếp hoặc bàn nhóm lớn nếu còn chỗ. Trợ lý không nên cam kết quán hoàn toàn yên tĩnh, nhất là khung 6:00 tối đến 8:00 tối.
- **related_menu_items:** Fresh Spring Rolls, Steamed Shrimp with Lemongrass (Tôm hấp sả), Orange Juice (Nước cam)
- **keywords:** quiet table, calm seating, date, family comfort, bàn yên tĩnh, chỗ ngồi yên tĩnh

## F040 — Can I split the bill or request a receipt?

- **category:** payments
- **intents:** split_bill, receipt, invoice, payment_support
- **question_en:** Can I split the bill or request a receipt?
- **question_vi:** Có thể chia hóa đơn hoặc xin hóa đơn không?
- **answer_en:** VietFood can support basic receipt requests and can help guests split payment informally when the group agrees how to divide the order. For official invoices or detailed business receipts, guests should ask staff before paying so the necessary information can be prepared correctly.
- **answer_vi:** VietFood có thể hỗ trợ xuất hóa đơn/biên nhận cơ bản và hỗ trợ nhóm chia tiền theo cách đơn giản nếu cả nhóm đã thống nhất. Với hóa đơn chính thức hoặc chứng từ chi tiết cho công ty, khách nên báo nhân viên trước khi thanh toán để chuẩn bị đúng thông tin.
- **related_menu_items:** Water (Nước lọc), Orange Juice (Nước cam)
- **keywords:** split bill, receipt, invoice, payment, hóa đơn, chia tiền, thanh toán nhóm

## Menu appendix (exact dish names aligned to current AVAILABLE menu)

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

## Retrieval tips

- Prefer the English answer when the user writes in English or asks simple tourist-style questions.
- Use the Vietnamese answer as fallback or for bilingual response generation.
- Match user intent using both `question_en` and `keywords`.
- Use `related_menu_items` to connect FAQ answers to live dish documents already stored in ChromaDB.
- If a dish is not marked AVAILABLE in the live database, prefer the live database over this synthetic FAQ file.