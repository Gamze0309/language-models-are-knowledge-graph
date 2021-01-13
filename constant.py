


found_invalid = [
    've', 'nun', 'dır', 'a', ',', 'için', 'ol', 'tarafından', 'birlikte', 'üzerinde', 'gibi', 'bu', 'buradan', ')', '(', 'hangi',
    'nın', 'nin', 'nün', 'dir', ';', '.', 'veya', 'ancak', 'ama', 'fakat', 'dur', 'hayır', 'değil', 'sonra', '"', 'içinde', 'ayrıca', 
    'iç', 'ara', 'gibi', 'ile', ':', 'yap', 'zaman', 'duğunda', 'sıra', 'nında', 'üzeri', 'diğinde', '2019', 
    'iyi', 'daha', '2020', 'üzerin', 'ora', 'bir', 'dür', 'tut', '2018', 'abilir', 'vasıta', '-', 
    'yap',  'dış', 'dığına', 'tık', 'adet', 'al', 'yukarı', 'başla', 'önce', 'hakkında',
    "'",  '4', '10', '3', '11', '&', '$', '12',  '2015', '2008','–', 'cak',
    'böylece', 'cek', 'tak', 'fazla', 'rağmen', 'çünkü', 'sebep', 'neden', 'sadece', '—',  '2007',  '2014', 'çoğun', '5', 'söyle', '2017', '20', 
    '2009',
]

invalid_relations = [
    've', 'ama', 'veya', 'böylece', 'çünkü', 'zaman', 'önce', 'rağmen', # conjunction
    'o', 'a', 'yuh', 'oha', 'çüş',
    'ne', 'nasıl', 'nere', 'ne zaman', 'kim', 'kime',
    'bir', 've', 'nun', 'dır', 
    'onların', 'o', 'onun', 'biz', 'bizim', 'onlar', # pronoun
    'on', 'yüz', 'bin', 'milyon', 'milyar',# unit
    'bir', 'iki', 'üç', 'dört', 'beş', 'altı', 'yedi', 'sekiz', 'dokuz',# number
    'yıl', 'ay', 'gün', 'günlük',
] + found_invalid



with open('corpus/turkish-adjectives.txt', 'r') as f:
    adjectives = [ line.strip().lower() for line in f]

with open('corpus/adverbs.txt', 'r') as f:
    adverbs = [ line.strip().lower() for line in f]

# with open('corpus/Wordlist-Verbs-All.txt', 'r') as f:
#     verbs = [ line.strip().lower() for line in f]

invalid_relations += adjectives
invalid_relations += adverbs
# invalid_relations += verbs

invalid_relations_set = set(invalid_relations)
