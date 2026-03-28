import json
import re
import os
import math

def format_time_ass(time_seconds):
    """Converts seconds to ASS time format H:MM:SS.cc"""
    if time_seconds < 0:
        time_seconds = 0
    hours = int(time_seconds // 3600)
    minutes = int((time_seconds % 3600) // 60)
    seconds = int(time_seconds % 60)
    centiseconds = int(round((time_seconds % 1) * 100))
    if centiseconds >= 100:
        centiseconds = 99
    return f"{hours:01}:{minutes:02}:{seconds:02}.{centiseconds:02}"


def rgb_to_ass_color(r, g, b, alpha="00"):
    """Converts RGB ints (0-255) to ASS &HAABBGGRR& format."""
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return f"&H{alpha}{b:02X}{g:02X}{r:02X}&".upper()


def hue_to_rgb(hue_deg):
    """Converts hue (0-360) to RGB values using full saturation/brightness."""
    h = hue_deg % 360
    s = 1.0
    v = 1.0
    hi = int(h / 60) % 6
    f = (h / 60) - int(h / 60)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)


def generate_ass_from_file(input_path, output_path, project_folder,
                           base_color, base_size, highlight_size, highlight_color,
                           words_per_block, gap_limit, mode, vertical_position, alignment,
                           font, outline_color, shadow_color, bold, italic, underline,
                           strikeout, border_style, outline_thickness, shadow_size, uppercase,
                           face_modes={}, remove_punctuation=True, rgb_mode=False):
    """
    Generates a single ASS file from a JSON input.
    Includes: RGB animation, bug-fixed timing, proper word-block logic.
    """

    # 1. Load Timeline Data
    filename = os.path.basename(input_path)
    base_name = os.path.splitext(filename)[0]

    renamed_timeline_name = base_name.replace("_processed", "") + "_timeline.json"
    renamed_timeline_path = os.path.join(project_folder, "final", renamed_timeline_name)

    timeline_data = None
    idx = None

    if os.path.exists(renamed_timeline_path):
        try:
            with open(renamed_timeline_path, "r") as tf:
                timeline_data = json.load(tf)
        except Exception:
            pass

    match_output = re.search(r"output(\d+)", filename)
    match_index = re.search(r"^(\d{3})_", filename)
    if match_output:
        idx = int(match_output.group(1))
    elif match_index:
        idx = int(match_index.group(1))

    if not timeline_data and idx is not None:
        csv_timeline = os.path.join(project_folder, "final",
                                    f"temp_video_no_audio_{idx}_timeline.json")
        if os.path.exists(csv_timeline):
            try:
                with open(csv_timeline, "r") as tf:
                    timeline_data = json.load(tf)
            except Exception:
                pass

    # 2. Face-mode overrides
    key = base_name
    if idx is not None:
        key = f"output{str(idx).zfill(3)}"

    current_alignment = alignment
    current_vertical_position = vertical_position

    mode_face = face_modes.get(key)
    if mode_face == "2" and not timeline_data:
        current_alignment = 5
        current_vertical_position = 0

    # 3. Load JSON
    try:
        with open(input_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
        segments_count = len(json_data.get('segments', []))
        print(f"[DEBUG] Loaded {input_path}: Found {segments_count} segments.")
    except Exception as e:
        print(f"[ERROR] Loading JSON {input_path}: {e}")
        return

    # 4. Normalize mode aliases for better stability across older configs.
    mode_aliases = {
        "palavra_por_palavra": "word_by_word",
        "wordbyword": "word_by_word",
        "sem_higlight": "no_highlight",
        "sem_highlight": "no_highlight",
    }
    mode = mode_aliases.get(str(mode).strip().lower(), mode)

    # 5. Detect RGB mode
    _rgb_active = rgb_mode or str(base_color).upper() in ("RGB", "RAINBOW", "&HRGB&")

    # 6. Prepare colours for header
    if _rgb_active:
        _hdr_r, _hdr_g, _hdr_b = hue_to_rgb(0)
        _hdr_color = rgb_to_ass_color(_hdr_r, _hdr_g, _hdr_b)
    else:
        _hdr_color = base_color if str(base_color).startswith("&H") else "&H00FFFFFF&"

    _hdr_hc = highlight_color if str(highlight_color).startswith("&H") else "&H0000FF00&"
    _out_c = outline_color if str(outline_color).startswith("&H") else "&H00000000&"
    _shd_c = shadow_color if str(shadow_color).startswith("&H") else "&H00000000&"

    # 7. Write ASS header
    header_ass = f"""[Script Info]
Title: ViralCutter Subtitles
ScriptType: v4.00+
PlayDepth: 0
PlayResX: 360
PlayResY: 640
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{base_size},{_hdr_color},&H00000000,{_out_c},{_shd_c},{bold},{italic},{underline},{strikeout},100,100,0,0,{border_style},{outline_thickness},{shadow_size},{alignment},-2,-2,{vertical_position},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    total_lines_written = 0
    word_global_index = 0

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header_ass)
        last_end_time = 0.0

        for segment in json_data.get('segments', []):
            words = segment.get('words', [])

            # Fix: fill missing timings
            timed_words = []
            for w in words:
                if 'word' not in w:
                    continue
                w = dict(w)
                if 'start' not in w or 'end' not in w:
                    prev_end = timed_words[-1].get('end', last_end_time) if timed_words else last_end_time
                    w.setdefault('start', prev_end)
                    w.setdefault('end', w['start'] + 0.3)
                timed_words.append(w)

            total_words = len(timed_words)
            i = 0

            while i < total_words:
                block = []
                while len(block) < words_per_block and i < total_words:
                    current_word = timed_words[i]
                    raw_word = current_word.get('word', '')

                    if remove_punctuation:
                        cleaned = re.sub(r'[.,!?;:\-]', '', raw_word).strip()
                    else:
                        cleaned = raw_word.strip()

                    if not cleaned:
                        i += 1
                        continue

                    entry = dict(current_word)
                    entry['word'] = cleaned

                    # Merge next word if it lacks timing
                    if i + 1 < total_words:
                        nxt = timed_words[i + 1]
                        if 'start' not in nxt or float(nxt.get('start', -1)) < 0:
                            nxt_w = nxt.get('word', '')
                            if remove_punctuation:
                                nxt_w = re.sub(r'[.,!?;:\-]', '', nxt_w).strip()
                            if nxt_w:
                                entry['word'] += " " + nxt_w
                            i += 1

                    block.append(entry)
                    i += 1

                if not block:
                    break

                if uppercase:
                    for w_item in block:
                        w_item['word'] = w_item['word'].upper()

                for j, current_word_data in enumerate(block):
                    start_sec = float(current_word_data.get('start', last_end_time))
                    end_sec = float(current_word_data.get('end', start_sec + 0.3))

                    # Fix timing collisions
                    if 0 < (start_sec - last_end_time) < gap_limit:
                        start_sec = last_end_time
                    if start_sec < last_end_time:
                        start_sec = last_end_time
                    if end_sec <= start_sec:
                        end_sec = start_sec + 0.15
                    # Keep subtitle durations readable and stable.
                    end_sec = max(end_sec, start_sec + 0.08)
                    end_sec = min(end_sec, start_sec + 5.0)

                    start_time_ass = format_time_ass(start_sec)
                    end_time_ass = format_time_ass(end_sec)
                    last_end_time = end_sec

                    # Build line
                    if mode == "highlight":
                        if _rgb_active:
                            parts = []
                            for k, wd in enumerate(block):
                                h_off = (start_sec * 60 + word_global_index * 45 + k * 60) % 360
                                if k == j:
                                    r1,g1,b1 = hue_to_rgb(h_off)
                                    r2,g2,b2 = hue_to_rgb((h_off + 80) % 360)
                                    c1 = rgb_to_ass_color(r1,g1,b1)
                                    c2 = rgb_to_ass_color(r2,g2,b2)
                                    parts.append(
                                        f"{{\\fs{highlight_size}\\c{c1}\\t(0,50,\\c{c2})}}{wd['word']} "
                                    )
                                else:
                                    h_off2 = (h_off + 180) % 360
                                    r1,g1,b1 = hue_to_rgb(h_off2)
                                    r2,g2,b2 = hue_to_rgb((h_off2 + 80) % 360)
                                    c1 = rgb_to_ass_color(r1,g1,b1)
                                    c2 = rgb_to_ass_color(r2,g2,b2)
                                    parts.append(
                                        f"{{\\fs{base_size}\\c{c1}\\t(0,50,\\c{c2})}}{wd['word']} "
                                    )
                            line = "".join(parts).strip()
                        else:
                            parts = []
                            for k, wd in enumerate(block):
                                if k == j:
                                    parts.append(f"{{\\fs{highlight_size}\\c{_hdr_hc}}}{wd['word']} ")
                                else:
                                    parts.append(f"{{\\fs{base_size}\\c{_hdr_color}}}{wd['word']} ")
                            line = "".join(parts).strip()

                    elif mode == "no_highlight":
                        if _rgb_active:
                            h_off = (start_sec * 60 + word_global_index * 30) % 360
                            r1,g1,b1 = hue_to_rgb(h_off)
                            r2,g2,b2 = hue_to_rgb((h_off + 90) % 360)
                            c1 = rgb_to_ass_color(r1,g1,b1)
                            c2 = rgb_to_ass_color(r2,g2,b2)
                            words_text = " ".join(wd['word'] for wd in block)
                            line = f"{{\\c{c1}\\t(0,60,\\c{c2})}}{words_text}"
                        else:
                            line = " ".join(wd['word'] for wd in block).strip()

                    elif mode == "word_by_word":
                        word_text = block[j]['word'].strip()
                        if _rgb_active:
                            h_off = (start_sec * 60 + word_global_index * 50 + j * 72) % 360
                            r1,g1,b1 = hue_to_rgb(h_off)
                            r2,g2,b2 = hue_to_rgb((h_off + 120) % 360)
                            r3,g3,b3 = hue_to_rgb((h_off + 240) % 360)
                            c1 = rgb_to_ass_color(r1,g1,b1)
                            c2 = rgb_to_ass_color(r2,g2,b2)
                            c3 = rgb_to_ass_color(r3,g3,b3)
                            line = f"{{\\c{c1}\\t(0,33,\\c{c2})\\t(33,66,\\c{c3})}}{word_text}"
                        else:
                            line = word_text
                    else:
                        line = " ".join(wd['word'] for wd in block).strip()

                    # Face tracking override
                    pos_tag = ""
                    if timeline_data:
                        mid_time = (start_sec + end_sec) / 2
                        found_mode = "1"
                        for seg in timeline_data:
                            if seg['start'] <= mid_time <= seg['end']:
                                found_mode = seg['mode']
                                break
                        if found_mode == "2":
                            pos_tag = f"{{\\an5\\pos(180,320)}}"

                    final_line = f"{pos_tag}{line}"
                    f.write(
                        f"Dialogue: 0,{start_time_ass},{end_time_ass},"
                        f"Default,,0,0,0,,{final_line}\n"
                    )
                    total_lines_written += 1
                    word_global_index += 1

    if total_lines_written == 0:
        print(f"[WARN] No dialogue lines written for {input_path}")
    else:
        print(f"[DEBUG] Wrote {total_lines_written} lines to {output_path}")


def adjust(base_color, base_size, highlight_size, highlight_color, words_per_block,
           gap_limit, mode, vertical_position, alignment, font, outline_color,
           shadow_color, bold, italic, underline, strikeout, border_style,
           outline_thickness, shadow_size, uppercase=False, project_folder="tmp", **kwargs):

    input_dir = os.path.join(project_folder, "subs")
    output_dir = os.path.join(project_folder, "subs_ass")
    os.makedirs(output_dir, exist_ok=True)

    remove_punctuation = kwargs.get('remove_punctuation', True)
    rgb_mode = kwargs.get('rgb_mode', False)

    face_modes = {}
    modes_file = os.path.join(project_folder, "face_modes.json")
    if os.path.exists(modes_file):
        try:
            with open(modes_file, "r") as f:
                face_modes = json.load(f)
            print("Loaded face modes for dynamic subtitle positioning.")
        except Exception as e:
            print(f"Could not load face modes: {e}")

    if not os.path.exists(input_dir):
        print(f"[ERROR] Subtitle folder missing: {input_dir}")
        raise FileNotFoundError(
            f"Subtitle folder missing at {input_dir}. "
            f"Ensure transcription completed successfully."
        )

    processed = 0
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + ".ass"
            output_path = os.path.join(output_dir, output_filename)

            generate_ass_from_file(
                input_path, output_path, project_folder,
                base_color, base_size, highlight_size, highlight_color,
                words_per_block, gap_limit, mode, vertical_position, alignment,
                font, outline_color, shadow_color, bold, italic, underline,
                strikeout, border_style, outline_thickness, shadow_size, uppercase,
                face_modes, remove_punctuation, rgb_mode
            )
            print(f"Processed: {filename} -> {output_filename}")
            processed += 1

    if processed == 0:
        print(f"[WARN] No JSON files found in {input_dir}")
    else:
        print(f"All {processed} JSON files processed and converted to ASS.")
