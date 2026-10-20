// @ts-check
// The shared max-models docs setup (@max-models/starlight-theme): served at
// https://max-models.github.io/slurm-script-generator/, with math, the API reference and a link check.
import { defineDocs } from '@max-models/starlight-theme';

export default defineDocs({
	repo: 'slurm-script-generator',
	title: 'slurm-script-generator',
	description: 'Generate, submit and monitor SLURM jobs from Python or the command line.',
	pythonPackage: 'slurm_script_generator',
	nav: [
		{ label: 'Getting started', link: '/getting-started/installation/' },
		{ label: 'Command line', link: '/cli/generate-slurm-script/' },
		{ label: 'Tutorials', link: '/tutorials/' },
		{ label: 'Development', link: '/development/docs/' },
		{ label: 'API', link: '/api/slurm_script_generator/', section: '/api/' },
	],
	sidebar: [
		{
			label: 'Getting started',
			items: [
				{ label: 'Installation', slug: 'getting-started/installation' },
				{ label: 'Quickstart', slug: 'getting-started/quickstart' },
			],
		},
		{
			label: 'Command line',
			items: [
				{ label: 'generate-slurm-script', slug: 'cli/generate-slurm-script' },
				{ label: 'slurm-template', slug: 'cli/slurm-template' },
				{ label: 'slurm-queue and friends', slug: 'cli/slurm-queue' },
			],
		},
		{ label: 'Tutorials', items: [{ autogenerate: { directory: 'tutorials' } }] },
		{ label: 'Development', items: [{ label: 'Building the docs', slug: 'development/docs' }] },
	],
	astro: {
		// the pages of the Sphinx site
		redirects: {
			'/cli.html': '/cli/generate-slurm-script/',
			'/slurm_template.html': '/cli/slurm-template/',
			'/slurm_queue.html': '/cli/slurm-queue/',
			'/tutorials.html': '/tutorials/',
			'/tutorials/00_basics.html': '/tutorials/00-basics/',
			'/tutorials/01_importing_scripts.html': '/tutorials/01-importing-scripts/',
			'/tutorials/02_queue_and_history.html': '/tutorials/02-queue-and-history/',
			'/api/index.html': '/api/slurm_script_generator/',
		},
	},
});
