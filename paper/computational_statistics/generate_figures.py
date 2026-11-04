"""Presentation-only figures from immutable evidence; no fitting or simulation."""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / 'figures'


def source_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def model_selection(decision):
    mr = decision['model_recovery']
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.3), layout='constrained')
    axes[0].bar(['Paired BIC winners'], [mr['winner_matches'] / mr['total_cases']], color='0.55', edgecolor='black')
    axes[0].text(0, 0.5, f"{mr['winner_matches']}/{mr['total_cases']}", ha='center', fontsize=13)
    axes[0].set_title('(a) Implementation agreement', fontsize=10)
    axes[1].bar(['MATLAB', 'HGFX'], [mr['matlab_balanced_accuracy'], mr['hgfx_balanced_accuracy']], color=['white', '0.65'], edgecolor='black', hatch='//')
    axes[1].axhline(decision['criteria_unchanged']['model_balanced_accuracy_min'], color='black', ls='--', label='Recovery threshold')
    axes[1].set_title('(b) Generating-model recovery', fontsize=10)
    axes[1].legend(fontsize=8, loc='lower right')
    for ax in axes:
        ax.set_ylim(0, 1.07)
        ax.set_ylabel('Fraction')
        ax.spines[['top', 'right']].set_visible(False)
    return fig


def recovery(decision):
    models = ['hgf_binary', 'ehgf_binary', 'uhgf_binary']
    metrics = [('convergence_rate', 'Convergence', 'convergence_rate_min'),
               ('median_correlation', 'Median correlation', 'median_correlation_min'),
               ('median_standardized_rmse', 'Median sRMSE', 'median_standardized_rmse_max')]
    fig, axes = plt.subplots(1, 3, figsize=(6.8, 2.9), layout='constrained')
    import numpy as np
    x = np.arange(3)
    for ax, (metric, title, criterion) in zip(axes, metrics):
        for offset, impl, color, hatch in [(-.18, 'matlab', 'white', ''), (.18, 'hgfx', '.65', '//')]:
            values = [decision['parameter_recovery'][m][impl][metric] for m in models]
            ax.bar(x+offset, values, .36, color=color, edgecolor='black', hatch=hatch, label='MATLAB' if impl == 'matlab' else 'HGFX')
        ax.axhline(decision['criteria_unchanged'][criterion], color='black', ls='--', lw=1)
        ax.set_xticks(x, ['HGF', 'eHGF', 'uHGF'])
        ax.set_title(title, fontsize=10)
        ax.spines[['top', 'right']].set_visible(False)
    axes[0].legend(fontsize=8, loc='lower right')
    return fig


def pyhgf_trajectories(raw):
    import numpy as np
    fig, axes = plt.subplots(3, 1, figsize=(6.8, 4.6), sharex=True, layout='constrained')
    for ax, field, label in zip(axes, ['first_level_predicted_probability', 'level_2_posterior_mean'], ['Predicted p(u=1)', 'Level-2 mean']):
        h = np.asarray(raw['hgfx']['fields'][field])
        p = np.asarray(raw['pyhgf']['fields'][field])
        ax.plot(np.arange(1, h.size+1), h, color='black', label='HGFX')
        ax.plot(np.arange(1, p.size+1), p, color='.6', ls='--', label='pyhgf 0.3.2')
        ax.set_ylabel(label)
    delta = np.asarray(raw['hgfx']['fields']['level_2_posterior_mean']) - np.asarray(raw['pyhgf']['fields']['level_2_posterior_mean'])
    axes[2].plot(np.arange(1, delta.size+1), delta, color='black', lw=.8)
    axes[2].set_ylabel('Mean difference')
    axes[2].set_xlabel('Trial')
    axes[0].legend(fontsize=8, loc='upper right')
    return fig


def empirical_workflow(result, inputs):
    import numpy as np
    mu, predicted = np.asarray(result['mu']), np.asarray(result['muhat'])
    assert result['status'] == 'COMPLETED_DESCRIPTIVE_WORKFLOW'
    assert mu.shape == predicted.shape == (len(inputs), 2)
    fig, axes = plt.subplots(2, 1, figsize=(6.8, 4.2), sharex=True, layout='constrained')
    x = np.arange(1, len(inputs)+1)
    axes[0].plot(x, inputs, color='.65', lw=1.1, label='Observed exchange rate')
    axes[0].plot(x, predicted[:, 0], color='black', lw=.8, ls='--', label='One-step predicted mean')
    axes[0].set_ylabel('CHF per USD')
    axes[0].legend(fontsize=8)
    axes[1].plot(x, mu[:, 1], color='black', lw=1)
    axes[1].set_ylabel('Level-2 posterior mean')
    axes[1].set_xlabel('Observation number')
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
    return fig


def main():
    OUT.mkdir(exist_ok=True)
    evidence = ROOT / 'reference/validation/m18_s7_reference_limitation/decision.json'
    fig = model_selection(json.loads(evidence.read_text()))
    outputs = []
    for suffix in ['png', 'pdf']:
        path = OUT / f'fig_model_selection.{suffix}'
        fig.savefig(path, dpi=300, bbox_inches='tight', metadata={'CreationDate': None, 'ModDate': None} if suffix == 'pdf' else None)
        outputs.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    plt.close(fig)
    example = OUT.parent / 'empirical_example'
    import numpy as np
    generated = empirical_workflow(json.loads((example / 'result.json').read_text()), np.loadtxt(example / 'example_usdchf.txt'))
    for suffix in ['png', 'pdf']:
        path = OUT / f'fig_usdchf_workflow.{suffix}'
        generated.savefig(path, dpi=300, bbox_inches='tight', metadata={'CreationDate': None, 'ModDate': None} if suffix == 'pdf' else None)
        outputs.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'source': 'released-wheel empirical example; no new MATLAB parity'})
    plt.close(generated)
    raw_path = ROOT / 'paper/reproducibility/p2a10_raw_numeric_result_35268575414.json'
    for name, generated in [('fig_recovery_metrics', recovery(json.loads(evidence.read_text()))),
                            ('fig_pyhgf_common_scope', pyhgf_trajectories(json.loads(raw_path.read_text())))]:
        for suffix in ['png', 'pdf']:
            path = OUT / f'{name}.{suffix}'
            generated.savefig(path, dpi=300, bbox_inches='tight')
            outputs.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'source': evidence.relative_to(ROOT).as_posix() if 'recovery' in name else raw_path.relative_to(ROOT).as_posix()})
        plt.close(generated)
    fig, ax = plt.subplots(figsize=(6.8, 2.8), layout='constrained')
    ax.set_axis_off()
    boxes = [(0.02, 0.66, 'Inputs and\nresponses'), (0.35, 0.66, 'Perceptual +\nresponse model'), (0.69, 0.66, 'Fit and\ndiagnostics'), (0.35, 0.13, 'Frozen MATLAB oracle\npaired checks')]
    for x, y, label in boxes:
        ax.text(x + .14, y, label, ha='center', va='center', fontsize=10,
                bbox={'boxstyle': 'round,pad=0.5', 'fc': 'white', 'ec': 'black'})
    for start, end in [((.28, .66), (.34, .66)), ((.62, .66), (.68, .66)), ((.49, .28), (.49, .49))]:
        ax.annotate('', xy=end, xytext=start, arrowprops={'arrowstyle': '->', 'color': 'black'})
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    for suffix in ['png', 'pdf']:
        path = OUT / f'fig_workflow.{suffix}'
        fig.savefig(path, dpi=300, bbox_inches='tight')
        outputs.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'source': 'conceptual workflow; no numerical data'})
    plt.close(fig)
    # Existing plots retain their exact values and scope; local copies allow a
    # portable candidate package without touching historical figure outputs.
    import shutil
    for name in ['fig_gpu_applicability', 'fig_p3_horizon_diagnostics']:
        for suffix in ['png', 'pdf']:
            source = ROOT / f'paper/figures/{name}.{suffix}'
            target = OUT / source.name
            shutil.copyfile(source, target)
            outputs.append({'path': target.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'source': source.relative_to(ROOT).as_posix()})
    (OUT / 'manifest.json').write_text(json.dumps({'hash_convention': 'text LF; binary exact', 'inputs': {p.relative_to(ROOT).as_posix(): source_sha(p) for p in [evidence, raw_path, example / 'result.json', example / 'example_usdchf.txt']}, 'operation': 'separate agreement/accuracy; grayscale recovery; raw pyhgf residual; empirical USD/CHF workflow; historical diagnostic figures byte-identical', 'outputs': outputs}, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
