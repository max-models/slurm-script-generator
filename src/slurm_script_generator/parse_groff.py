import re

def clean_groff(text: str) -> str:
    # Remove font macros like \fB...\fR or \fI...\fR
    text = re.sub(r'\\f[BI](.*?)\\fR', r'\1', text)
    # Remove any remaining font switches (e.g., \fB, \fI, \fR)
    text = re.sub(r'\\f[BRI]', '', text)
    # Replace escaped dash
    text = text.replace(r'\-', '-')
    # Normalize whitespace
    return re.sub(r'\s+', ' ', text).strip()

def parse_entry(lines):
    # First line after .TP: flags/options
    flags_line = clean_groff(lines[0])
    # Split by comma, strip whitespace
    flags = [f.strip() for f in flags_line.split(",")]
    # Join rest of lines as description, clean formatting
    desc = " ".join(clean_groff(line) for line in lines[1:])
    return flags, desc


with open('sbatch.1','r') as f:
    lines = f.readlines()

tp_level = 0
start_options = False
entry_started = False
ignore = False
for iline, line in enumerate(lines):
    # print(iline, line[:-1])
    if '.SH "OPTIONS"' in line:
        start_options = True
    
    if start_options:
        if line[:3] == '.RS':
            ignore = True
        elif line[:3] == '.RE':
            ignore = False

        if not ignore:
            if line[:3] == '.TP':
                start_entry = iline
                entry_started = True
                tp_level += 1
            elif line[:3] == '.IP' and entry_started:
                tp_level -= 1

            if tp_level == 0 and entry_started:
                end_entry = iline
                entry = lines[start_entry+1:end_entry]
                # print(f"{start_entry = }")
                flags, description = parse_entry(entry)
                print("Flags:", flags)
                print("Description:", description)
                entry_started = False
            

# print(lines)

with open('test.groff','r') as f:
    entry= f.readlines()

flags, description = parse_entry(entry)
print("Flags:", flags)
print("Description:", description)
