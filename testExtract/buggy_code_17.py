from typing import List


def parse_music(music_string: str) -> List[int]:
    note_map = {'o': 3, 'o|': 2, '.|': 1}
    return [note_map[x] for x in music_string.split(' ') if x]


from typing import List   # 未分解语句
def parse_music(music_string: str):
    note_map = {'o': 3, 'o|': 2, '.|': 1}
    x1 = []
    x2 = music_string.split(' ')
    for x in x2:
        if x:
            x3 = note_map[x]
            x1.append(x3)
    return x1