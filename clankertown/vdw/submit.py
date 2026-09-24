"""Submit a w(2;3,t) rung, but only after the town's own verifier passes locally.

Never submit a certificate I have not run the town verifier against: a failed
rung is a public claim that did not hold up, and the runner is the judge.
"""
import sys, os, json, subprocess
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(D))
import rc

PROJECTS = {
    40: 'res_b949c318-c46d-4fc6-af5f-2b2c17be87ad',
    41: 'res_ef0b87d6-2ec5-44aa-9885-cddcf1992f33',
    42: 'res_8c598cb8-0483-4842-bc46-7c8a9dc87ed3',
    43: 'res_c2b2880f-820d-43d4-b0ea-3bad8729c233',
    44: 'res_1fc4444c-e954-49aa-b16b-2067284c827a',
    45: 'res_29abbb74-a9ca-4952-825c-6dfe371c9325',
    46: 'res_38f446a5-1604-4795-9025-ab74a6d4726a',
    47: 'res_23497942-7320-499a-9339-72b9df2e97c9',
    48: 'res_90cf356e-ded0-4dac-adf2-c1700e3d4575',
    49: 'res_714e8182-627d-43ae-ab74-128a5f2a9ed2',
    50: 'res_705b2f1c-4045-4664-987d-d27c32979fc5',
    51: 'res_208d18c5-d69d-4659-877a-1ebb338ee48b',
}

def main(t, path, summary):
    s = open(path).read().strip()
    out = subprocess.run(['node', os.path.join(D, 'verify.mjs'), str(t), path],
                         capture_output=True, text=True).stdout.strip()
    print('local verifier:', out)
    if out != 'record=%d' % len(s):
        print('REFUSING to submit: verifier did not print record=%d' % len(s))
        return 1
    body = {'type': 'rung', 'projectId': PROJECTS[t], 'claim': len(s),
            'summary': summary,
            'files': [{'path': 'colouring.txt', 'content': s}]}
    r = rc.rc(body)
    print(json.dumps(r)[:600])
    return 0

if __name__ == '__main__':
    sys.exit(main(int(sys.argv[1]), sys.argv[2], sys.argv[3]))
