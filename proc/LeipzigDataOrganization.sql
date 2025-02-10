WITH JointWords AS (
				SELECT  CONCAT(Word1, " ", Word2) as Word, SUM(Freq) as Freq 
						FROM (
									SELECT w.Word AS Word1,  ww.Word as Word2, n.Freq
										FROM "deu-de_web-public_2019_1M-co_n" AS 'n'
										
										LEFT JOIN "deu-de_web-public_2019_1M-words" AS 'w'
											ON n.Word1_ID = w.ID
										
										LEFT JOIN "deu-de_web-public_2019_1M-words" AS 'ww'
											ON n.Word2_ID = ww.ID
											
										UNION ALL
										
										SELECT w.Word AS Word1,  ww.Word as Word2, n.Freq
										FROM "deu_wikipedia_2021_1M-co_n" AS 'n'
										
										LEFT JOIN "deu_wikipedia_2021_1M-words" AS 'w'
											ON n.Word1_ID = w.ID
										
										LEFT JOIN "deu_wikipedia_2021_1M-words" AS 'ww'
											ON n.Word2_ID = ww.ID
											
										UNION ALL
										
											SELECT w.Word AS Word1,  ww.Word as Word2, n.Freq
										FROM "deu_news_2024_1M-co_n" AS 'n'
										
										LEFT JOIN "deu_news_2024_1M-words" AS 'w'
											ON n.Word1_ID = w.ID
										
										LEFT JOIN "deu_news_2024_1M-words" AS 'ww'
											ON n.Word2_ID = ww.ID
											
										UNION ALL
					
										SELECT w.Word AS Word1,  ww.Word as Word2, n.Freq
										FROM "deu-de_web_2021_1M-co_n" AS 'n'
										
										LEFT JOIN "deu-de_web_2021_1M-words" AS 'w'
											ON n.Word1_ID = w.ID
										
										LEFT JOIN "deu-de_web_2021_1M-words" AS 'ww'
											ON n.Word2_ID = ww.ID
											
											) 
						GROUP BY Word1, Word2 
					),
					
		SingleWords AS (
					SELECT Word, sum(Freq) as Freq 
						FROM (
								SELECT * FROM "deu-de_web-public_2019_1M-words"

								UNION ALL 

								SELECT * FROM "deu-de_web_2021_1M-words"

								UNION ALL 

								SELECT * FROM "deu_news_2024_1M-words"

								UNION ALL 

								SELECT * FROM "deu_wikipedia_2021_1M-words"
								)
							GROUP BY Word
						),
										
		Names AS (
			SELECT * FROM "StadtFlussnames"
			)
			
			SELECT * 
					FROM Names AS 'n'
			
			LEFT JOIN (
						SELECT * FROM JointWords
						UNION ALL
						SELECT * FROM SingleWords
						) AS 'w'
				ON w.Word = n.word
				
				WHERE w.Word is not null
								
								
								