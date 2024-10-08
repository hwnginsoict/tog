extract_question_entity = """Hãy trích xuất tất cả các thực thể có tên riêng trong câu hỏi sau. Các thực thể có thể bao gồm tên người, tổ chức, địa danh, quốc gia, hay các thực thể khác. Nếu có tên riêng chỉ trích xuất tên riêng.

Câu hỏi: {}

Ví dụ:
Câu hỏi: "Lê Hồng Việt là ai và vai trò của ông trong Khối sản phẩm AI của công ty FPT Smart Cloud là gì?"
Thực thể: {Lê Hồng Việt, Khối sản phẩm AI, FPT Smart Cloud}

Hãy trích xuất thực thể từ câu hỏi: {}
Thực thể:
"""

extract_relation_prompt = """Vui lòng trích xuất %s relation (phân cách bằng dấu chấm phẩy) có liên quan đến câu hỏi và đánh giá mức độ đóng góp của chúng trên thang Score từ 0 đến 1 (tổng Score của %s relation là 1).
Q: Tên của tổng thống của quốc gia mà ngôn ngữ chính được nói là Brahui vào năm 1980?
entity chủ đề: Ngôn ngữ Brahui
Các relation: language.human_language.main_country; language.human_language.language_family; language.human_language.iso_639_3_code; base.rosetta.languoid.parent; language.human_language.writing_system; base.rosetta.languoid.languoid_class; language.human_language.countries_spoken_in; kg.object_profile.prominent_type; base.rosetta.languoid.document; base.ontologies.ontology_instance.equivalent_instances; base.rosetta.languoid.local_name; language.human_language.region
A: 1. {language.human_language.main_country (Score: 0.4)}: relation này rất quan trọng vì nó liên quan trực tiếp đến quốc gia mà tổng thống được hỏi, và quốc gia chính nơi ngôn ngữ Brahui được nói vào năm 1980.
2. {language.human_language.countries_spoken_in (Score: 0.3)}: relation này cũng quan trọng vì nó cung cấp thông tin về các quốc gia nơi ngôn ngữ Brahui được nói, có thể giúp thu hẹp phạm vi tìm kiếm tổng thống.
3. {base.rosetta.languoid.parent (Score: 0.2)}: relation này ít quan trọng hơn nhưng vẫn cung cấp một số bối cảnh về họ ngôn ngữ mà Brahui thuộc về, có thể hữu ích trong việc hiểu bối cảnh ngôn ngữ và văn hóa của quốc gia được hỏi.

Q:
"""

score_entity_candidates_prompt = """Vui lòng đánh giá mức độ đóng góp của các entity đối với câu hỏi trên thang Score từ 0 đến 1 (tổng Score của tất cả các entity là 1).
Q: Bộ phim có sự tham gia của Miley Cyrus và được sản xuất bởi Tobin Armbrust?
Relation: film.producer.film
Entity: The Resident; So Undercover; Let Me In; Begin Again; The Quiet Ones; A Walk Among the Tombstones
Score: 0.0, 1.0, 0.0, 0.0, 0.0, 0.0
Bộ phim phù hợp với các tiêu chí đã cho là "So Undercover" có Miley Cyrus và được sản xuất bởi Tobin Armbrust. Do đó, Score cho "So Undercover" sẽ là 1 và Score cho tất cả các entity khác sẽ là 0.

Q: {}
Relation: {}
Entity:
"""

answer_prompt = """Dựa vào câu hỏi và các bộ ba đồ thị tri thức liên quan (entity, relation, entity), bạn được yêu cầu trả lời câu hỏi với các bộ ba này và kiến thức của bạn.
Q: Tìm người đã nói "Taste cannot be controlled by law", người đó đã chết vì gì?
Bộ ba tri thức: "Taste cannot be controlled by law.", media_common.quotation.author, Thomas Jefferson
A: Dựa trên các bộ ba tri thức đã cho, không đủ để trả lời toàn bộ câu hỏi. Bộ ba chỉ cung cấp thông tin về người đã nói "Taste cannot be controlled by law", đó là Thomas Jefferson. Để trả lời phần thứ hai của câu hỏi, cần có thêm kiến thức về nơi Thomas Jefferson qua đời.

Q:

"""

prompt_evaluate="""Cho một câu hỏi và các triplet đồ thị tri thức liên quan (entity, relation, entity), bạn được yêu cầu trả lời liệu thông tin này có đủ để trả lời câu hỏi với các triplet này và kiến thức của bạn hay không (Yes or No).
Q: Tìm người đã nói "Taste cannot be controlled by law", người này đã chết vì lý do gì?
Knowledge Triplets: Taste cannot be controlled by law., media_common.quotation.author, Thomas Jefferson
A: {No}. Dựa trên các triplet tri thức được cung cấp, không đủ để trả lời toàn bộ câu hỏi. Các triplet chỉ cung cấp thông tin về người đã nói "Taste cannot be controlled by law," đó là Thomas Jefferson. Để trả lời phần còn lại của câu hỏi, cần có thêm thông tin về nơi Thomas Jefferson qua đời.

Q: Nghệ sĩ được đề cử cho The Long Winter đã sống ở đâu?
Knowledge Triplets: The Long Winter, book.written_work.author, Laura Ingalls Wilder
Laura Ingalls Wilder, people.person.places_lived, Unknown-Entity
Unknown-Entity, people.place_lived.location, De Smet
A: {Yes}. Dựa trên các triplet tri thức được cung cấp, tác giả của The Long Winter, Laura Ingalls Wilder, đã sống ở De Smet. Do đó, câu trả lời cho câu hỏi là {De Smet}.

Q: Huấn luyện viên của đội bóng thuộc sở hữu của Steve Bisciotti là ai?
Knowledge Triplets: Steve Bisciotti, sports.professional_sports_team.owner_s, Baltimore Ravens
Steve Bisciotti, sports.sports_team_owner.teams_owned, Baltimore Ravens
Steve Bisciotti, organization.organization_founder.organizations_founded, Allegis Group
A: {No}. Dựa trên các triplet tri thức được cung cấp, huấn luyện viên của đội bóng thuộc sở hữu của Steve Bisciotti không được đề cập rõ ràng. Tuy nhiên, có thể suy ra rằng đội bóng thuộc sở hữu của Steve Bisciotti là Baltimore Ravens, một đội thể thao chuyên nghiệp. Do đó, cần có thêm kiến thức về huấn luyện viên hiện tại của Baltimore Ravens để trả lời câu hỏi.

Q: Tỉnh Rift Valley nằm ở quốc gia sử dụng loại tiền tệ nào?
Knowledge Triplets: Rift Valley Province, location.administrative_division.country, Kenya
Rift Valley Province, location.location.geolocation, UnName_Entity
Rift Valley Province, location.mailing_address.state_province_region, UnName_Entity
Kenya, location.country.currency_used, Kenyan shilling
A: {Yes}. Dựa trên các triplet tri thức được cung cấp, tỉnh Rift Valley nằm ở Kenya, quốc gia sử dụng đồng shilling Kenya làm đơn vị tiền tệ. Do đó, câu trả lời cho câu hỏi là {Kenyan shilling}.

Q: Quốc gia có quốc ca của Bolivia giáp với những nước nào?
Knowledge Triplets: National Anthem of Bolivia, government.national_anthem_of_a_country.anthem, UnName_Entity
National Anthem of Bolivia, music.composition.composer, Leopoldo Benedetto Vincenti
National Anthem of Bolivia, music.composition.lyricist, José Ignacio de Sanjinés
UnName_Entity, government.national_anthem_of_a_country.country, Bolivia
Bolivia, location.country.national_anthem, UnName_Entity
A: {No}. Dựa trên các triplet tri thức được cung cấp, chúng ta có thể suy ra rằng Quốc ca của Bolivia là quốc ca của Bolivia. Tuy nhiên, các triplet tri thức được cung cấp không cung cấp thông tin về các quốc gia giáp ranh với Bolivia. Để trả lời câu hỏi này, cần có thêm kiến thức về địa lý của Bolivia và các nước láng giềng của nó.

"""

generate_directly = """Q: Bang nào là nơi có trường đại học được đại diện trong thể thao bởi đội bóng rổ nam George Washington Colonials?
A: Đầu tiên, cơ sở giáo dục có đội bóng rổ nam George Washington Colonials là Đại học George Washington. Thứ hai, Đại học George Washington nằm ở Washington D.C. Câu trả lời là {Washington, D.C.}.

Q: Ai liệt kê Pramatha Chaudhuri là người ảnh hưởng và đã viết Jana Gana Mana?
A: Đầu tiên, Bharoto Bhagyo Bidhata đã viết Jana Gana Mana. Thứ hai, Bharoto Bhagyo Bidhata liệt kê Pramatha Chaudhuri là người ảnh hưởng. Câu trả lời là {Bharoto Bhagyo Bidhata}.

Q: Nghệ sĩ nào được đề cử cho giải thưởng You Drive Me Crazy?
A: Đầu tiên, nghệ sĩ được đề cử cho giải thưởng You Drive Me Crazy là Britney Spears. Câu trả lời là {Jason Allen Alexander}.

Q: Người sinh ra ở Siegen đã ảnh hưởng đến tác phẩm của Vincent Van Gogh là ai?
A: Đầu tiên, Peter Paul Rubens, Claude Monet, và những người khác đã ảnh hưởng đến tác phẩm của Vincent Van Gogh. Thứ hai, Peter Paul Rubens sinh ra ở Siegen. Câu trả lời là {Peter Paul Rubens}.

Q: Quốc gia gần Nga nơi Mikheil Saakashvii nắm giữ vị trí trong chính phủ là gì?
A: Đầu tiên, Trung Quốc, Na Uy, Phần Lan, Estonia và Georgia là các quốc gia gần Nga. Thứ hai, Mikheil Saakashvii giữ chức vụ trong chính phủ của Georgia. Câu trả lời là {Georgia}.

Q: Loại thuốc nào mà diễn viên đã đóng vai Urethane Wheels Guy đã quá liều?
A: Đầu tiên, Mitchell Lee Hedberg đã đóng vai Urethane Wheels Guy. Thứ hai, Mitchell Lee Hedberg đã quá liều Heroin. Câu trả lời là {Heroin}."""

score_entity_candidates_prompt_wiki = """Hãy chấm Score đóng góp của các entity vào câu hỏi theo thang Score từ 0 đến 1 (tổng số Score của tất cả entity là 1).
Q: Staten Island Summer, có sự góp mặt của nữ diễn viên nào là thành viên của "Saturday Night Live"?
Relation: cast member
Entites: Ashley Greene; Bobby Moynihan; Camille Saviola; Cecily Strong; Colin Jost; Fred Armisen; Gina Gershon; Graham Phillips; Hassan Johnson; Jackson Nicoll; Jim Gaffigan; John DeLuca; Kate Walsh; Mary Birdsong
Score: 0.0, 0.0, 0.0, 0.4, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4, 0.0
Để chấm Score đóng góp của các entity vào câu hỏi, chúng ta cần xác định entity nào liên quan đến câu hỏi và có khả năng cao là câu trả lời chính xác.
Trong trường hợp này, chúng ta đang tìm kiếm một nữ diễn viên là thành viên của "Saturday Night Live" và đã tham gia bộ phim "Staten Island Summer." Dựa trên thông tin này, chúng ta có thể loại bỏ các entity không phải là nữ diễn viên hoặc không phải là thành viên của "Saturday Night Live."
Các entity liên quan đáp ứng tiêu chí này là:
- Ashley Greene
- Cecily Strong
- Fred Armisen
- Gina Gershon
- Kate Walsh

Để phân bổ Score, chúng ta có thể gán Score cao hơn cho các entity có khả năng cao là câu trả lời chính xác. Trong trường hợp này, câu trả lời có khả năng nhất sẽ là một nữ diễn viên từng là thành viên của "Saturday Night Live" vào thời Score bộ phim được phát hành.
Dựa trên lý luận này, Score có thể được phân bổ như sau:
- Ashley Greene: 0
- Cecily Strong: 0.4
- Fred Armisen: 0.2
- Gina Gershon: 0
- Kate Walsh: 0.4

Q: {}
Relation: {}
Entites: """

prompt_evaluate_wiki="""Với một câu hỏi và các triplet đồ thị tri thức được truy xuất liên quan (entity, relation, entity) hoặc (entity với relation, entity), đảm bảo rằng các triplet có relation chặt chẽ như làm việc tại ..., bạn được yêu cầu trả lời xem liệu nó có đủ để bạn trả lời câu hỏi với các triplet này và kiến thức của bạn không (Có hoặc Không).
Q: Viscount Yamaji Motoharu là một tướng trong Quân đội Đế quốc Nhật Bản thời kỳ đầu thuộc về Đế quốc nào?
Knowledge Triplets: Quân đội Đế quốc Nhật Bản, trung thành, Hoàng đế Nhật Bản
Yamaji Motoharu, trung thành, Hoàng đế Nhật Bản
Yamaji Motoharu, cấp bậc quân sự, tướng
A: {Yes}. Dựa trên các triplet tri thức được cung cấp và kiến thức của tôi, Viscount Yamaji Motoharu, người là một tướng trong Quân đội Đế quốc Nhật Bản thời kỳ đầu, thuộc về Đế quốc Nhật Bản. Do đó, câu trả lời cho câu hỏi là {Đế quốc Nhật Bản}.

Q: Huấn luyện viên của đội thuộc sở hữu của Steve Bisciotti là ai?
Knowledge Triplets: psilocybin, được mô tả bởi nguồn, Luật Opium,
psilocybin, được tìm thấy trong loài, Gymnopilus purpuratus,
psilocybin, được tìm thấy trong loài, Gymnopilus spectabilis, 
Luật Opium, là một phần của, norcodeine (cấu trúc lập thể được xác định),
Gymnopilus purpuratus, tính ăn được, nấm có tác dụng thần kinh,
Gymnopilus spectabilis, loài cha mẹ, Gymnopilus
A: {No}. Dựa trên các triplet tri thức được cung cấp và kiến thức của tôi, hợp chất cụ thể trong họ nấm Psilocybin chuyển đổi thành psilocin trong cơ thể không được đề cập rõ ràng. Do đó, cần thêm kiến thức về các hợp chất cụ thể và quá trình chuyển đổi chúng thành psilocin để trả lời câu hỏi.

Q: Vận động viên quần vợt nào trẻ hơn, John Newcombe hay Květa Peschke?
Knowledge Triplets: Květa Peschke, ngày sinh, +1975-07-09T00:00:00Z, 
John Newcombe, ngày sinh, +1944-05-23T00:00:00Z,
John Newcombe, quốc tịch, Úc
A: {Yes}. Dựa trên các triplet tri thức được cung cấp và kiến thức của tôi, John Newcombe sinh ngày 23 tháng 5 năm 1944, và Květa Peschke sinh ngày 9 tháng 7 năm 1975. Do đó, {Květa Peschke} trẻ hơn John Newcombe.

Q: Mychal George Thompson đã thi đấu tại sân nhà nào cùng với San Antonio Spurs?
Knowledge Triplets: San Antonio Spurs, sân nhà, AT&T Center
San Antonio Spurs, sân nhà, Alamodome
San Antonio Spurs, sân nhà, Fort Worth Convention Center
AT&T Center, đội chủ nhà, San Antonio Spurs
Fort Worth Convention Center, thuộc về đơn vị hành chính, Texas
Fort Worth Convention Center, đội chủ nhà, San Antonio Spurs
A: {Yes}. Dựa trên các triplet tri thức được cung cấp và kiến thức của tôi, Mychal George Thompson đã thi đấu tại sân nhà với San Antonio Spurs tại AT&T Center. Do đó, câu trả lời cho câu hỏi là {AT&T Center}.
"""

extract_relation_prompt_wiki = """Vui lòng truy xuất %s relation (tách biệt bằng dấu chấm phẩy) đóng góp vào câu hỏi và đánh giá mức độ đóng góp của chúng trên thang Score từ 0 đến 1 (tổng Score của %s relation là 1).
Q: Chú của Mesih Pasha trở thành hoàng đế vào năm nào?
entity chủ đề: Mesih Pasha
relation:
1. wiki.relation.child
2. wiki.relation.country_of_citizenship
3. wiki.relation.date_of_birth
4. wiki.relation.family
5. wiki.relation.father
6. wiki.relation.languages_spoken, written_or_signed
7. wiki.relation.military_rank
8. wiki.relation.occupation
9. wiki.relation.place_of_death
10. wiki.relation.position_held
11. wiki.relation.religion_or_worldview
12. wiki.relation.sex_or_gender
13. wiki.relation.sibling
14. wiki.relation.significant_event
A: 1. {wiki.relation.family (Score: 0.5)}: relation này rất liên quan vì nó có thể cung cấp thông tin về bối cảnh gia đình của Mesih Pasha, bao gồm cả chú của ông, người đã trở thành hoàng đế.
2. {wiki.relation.father (Score: 0.4)}: Chú là anh trai của cha, do đó relation với cha cũng có thể cung cấp thông tin liên quan.
3. {wiki.relation.position_held (Score: 0.1)}: relation này có mức độ liên quan vừa phải vì nó có thể cung cấp thông tin về các vị trí quan trọng mà Mesih Pasha hoặc chú của ông đã giữ liên quan đến việc trở thành hoàng đế.

Q: Viện Van Andel được thành lập một phần bởi doanh nhân người Mỹ nào, người nổi tiếng nhất với tư cách là đồng sáng lập của Tập đoàn Amway?
entity chủ đề: Viện Van Andel
relation:
1. wiki.relation.affiliation
2. wiki.relation.country
3. wiki.relation.donations
4. wiki.relation.educated_at
5. wiki.relation.employer
6. wiki.relation.headquarters_location
7. wiki.relation.legal_form
8. wiki.relation.located_in_the_administrative_territorial_entity
9. wiki.relation.total_revenue
A: 1. {wiki.relation.affiliation (Score: 0.4)}: relation này có liên quan vì nó có thể cung cấp thông tin về các cá nhân hoặc tổ chức liên quan đến Viện Van Andel, bao gồm cả doanh nhân người Mỹ đã đồng sáng lập Tập đoàn Amway.
2. {wiki.relation.donations (Score: 0.3)}: relation này có liên quan vì nó có thể cung cấp thông tin về các khoản đóng góp tài chính cho Viện Van Andel, có thể bao gồm các khoản quyên góp từ doanh nhân người Mỹ đang được đề cập.
3. {wiki.relation.educated_at (Score: 0.3)}: relation này có liên quan vì nó có thể cung cấp thông tin về nền tảng giáo dục của doanh nhân người Mỹ, điều có thể ảnh hưởng đến việc tham gia sáng lập Viện Van Andel.
"""

answer_prompt_wiki = """Với một câu hỏi và các triplet đồ thị tri thức được truy xuất liên quan (entity, relation, entity), bạn được yêu cầu trả lời câu hỏi với các triplet này và kiến thức của bạn.
Q: Viscount Yamaji Motoharu là một tướng trong Quân đội Đế quốc Nhật Bản thời kỳ đầu thuộc về Đế quốc nào?
Knowledge Triplets: Quân đội Đế quốc Nhật Bản, trung thành, Hoàng đế Nhật Bản
Yamaji Motoharu, trung thành, Hoàng đế Nhật Bản
Yamaji Motoharu, cấp bậc quân sự, tướng
A: Dựa trên các triplet tri thức được cung cấp và kiến thức của tôi, Viscount Yamaji Motoharu, người là một tướng trong Quân đội Đế quốc Nhật Bản thời kỳ đầu, thuộc về Đế quốc Nhật Bản. Do đó, câu trả lời cho câu hỏi là {Đế quốc Nhật Bản}.

Q: Huấn luyện viên của đội thuộc sở hữu của Steve Bisciotti là ai?
Knowledge Triplets: psilocybin, được mô tả bởi nguồn, Luật Opium,
psilocybin, được tìm thấy trong loài, Gymnopilus purpuratus,
psilocybin, được tìm thấy trong loài, Gymnopilus spectabilis, 
Luật Opium, là một phần của, norcodeine (cấu trúc lập thể được xác định), 
Gymnopilus purpuratus, tính ăn được, nấm có tác dụng thần kinh,
Gymnopilus spectabilis, loài cha mẹ, Gymnopilus
A: Dựa trên các triplet tri thức được cung cấp và kiến thức của tôi, hợp chất cụ thể trong họ nấm Psilocybin chuyển đổi thành psilocin trong cơ thể không được đề cập rõ ràng. Do đó, cần thêm kiến thức về các hợp chất cụ thể và quá trình chuyển đổi chúng thành psilocin để trả lời câu hỏi.

Q: Vận động viên quần vợt nào trẻ hơn, John Newcombe hay Květa Peschke?
Knowledge Triplets: Květa Peschke, ngày sinh, +1975-07-09T00:00:00Z, 
John Newcombe, ngày sinh, +1944-05-23T00:00:00Z,
John Newcombe, quốc tịch, Úc
A: Dựa trên các triplet tri thức được cung cấp và kiến thức của tôi, John Newcombe sinh ngày 23 tháng 5 năm 1944, và Květa Peschke sinh ngày 9 tháng 7 năm 1975. Do đó, {Květa Peschke} trẻ hơn John Newcombe.

Q: Mychal George Thompson đã thi đấu tại sân nhà nào cùng với San Antonio Spurs?
Knowledge Triplets: San Antonio Spurs, sân nhà, AT&T Center
San Antonio Spurs, sân nhà, Alamodome
San Antonio Spurs, sân nhà, Fort Worth Convention Center
AT&T Center, đội chủ nhà, San Antonio Spurs
Fort Worth Convention Center, thuộc về đơn vị hành chính, Texas
Fort Worth Convention Center, đội chủ nhà, San Antonio Spurs
A: Dựa trên các triplet tri thức được cung cấp và kiến thức của tôi, Mychal George Thompson đã thi đấu tại sân nhà với San Antonio Spurs tại AT&T Center. Do đó, câu trả lời cho câu hỏi là {AT&T Center}.

Q: {}
"""

cot_prompt = """Q: Bang nào là nơi mà trường đại học có đội bóng rổ nam George Washington Colonials đại diện trong các sự kiện thể thao?
A: Thứ nhất, cơ sở giáo dục có đội thể thao George Washington Colonials trong bóng rổ nam là Đại học George Washington. Thứ hai, Đại học George Washington nằm ở Washington D.C. Câu trả lời là {Washington, D.C.}.

Q: Ai liệt kê Pramatha Chaudhuri là người có ảnh hưởng và đã viết Jana Gana Mana?
A: Thứ nhất, Bharoto Bhagyo Bidhata đã viết Jana Gana Mana. Thứ hai, Bharoto Bhagyo Bidhata liệt kê Pramatha Chaudhuri là người có ảnh hưởng. Câu trả lời là {Bharoto Bhagyo Bidhata}.

Q: Nghệ sĩ nào đã được đề cử giải thưởng cho You Drive Me Crazy?
A: Thứ nhất, nghệ sĩ được đề cử giải thưởng cho You Drive Me Crazy là Britney Spears. Câu trả lời là {Jason Allen Alexander}.

Q: Người sinh ra ở Siegen đã ảnh hưởng đến tác phẩm của Vincent Van Gogh là ai?
A: Thứ nhất, Peter Paul Rubens, Claude Monet và những người khác đã ảnh hưởng đến tác phẩm của Vincent Van Gogh. Thứ hai, Peter Paul Rubens sinh ra ở Siegen. Câu trả lời là {Peter Paul Rubens}.

Q: Quốc gia gần Nga nơi Mikheil Saakashvili nắm giữ một vị trí trong chính phủ là quốc gia nào?
A: Thứ nhất, Trung Quốc, Na Uy, Phần Lan, Estonia và Georgia gần Nga. Thứ hai, Mikheil Saakashvili nắm giữ một vị trí trong chính phủ tại Georgia. Câu trả lời là {Georgia}.

Q: Loại ma túy nào đã khiến diễn viên đóng vai Urethane Wheels Guy dùng quá liều?
A: Thứ nhất, Mitchell Lee Hedberg đã đóng vai Urethane Wheels Guy. Thứ hai, Mitchell Lee Hedberg đã dùng quá liều Heroin. Câu trả lời là {Heroin}.
"""
