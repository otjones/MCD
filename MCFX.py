from os import path

lines = []

def init(total_in, total_out):
    lines.append(f'/convolver/new {total_in} {total_out} 4096 44100 1.0 \n')

def addLine(n_in, n_out):
    lines.append(f'/impulse/read/ {n_in+1} {n_out+1} 0 0 0 1 /source_{n_in}/impulse-{n_out}.wav\n')
    return lines

def export(outpath):
    with open(path.join(outpath, "mcfx.config"), 'w') as f:
        for line in lines:
            f.write(line)