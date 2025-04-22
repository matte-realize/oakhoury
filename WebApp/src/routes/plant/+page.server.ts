import { z } from 'zod';
import { message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { API_ROUTE } from '$lib/constants';

const schema = z.object({
	// treeId comes from the form as a string, coerce to number
	treeId: z.coerce.number().int().positive('Please select a tree type.'),
	siteDescription: z.string().nonempty('Please provide a brief site description.').max(500)
});

interface TreeOption {
	id: number;
	common_name: string;
	scientific_name: string;
}

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.user) {
		throw redirect(302, '/login');
	}
	// Load available tree types for the dropdown
	let availableTrees = [];
	const apiUrl = `${API_ROUTE}/trees`;
	const response = await fetch(apiUrl);
	if (!response.ok) {
		const errorBody = await response.text();
		console.error(`API Error (${response.status}): ${errorBody}`);
		throw error(500, {
			message: 'Failed to load tree types. Please try again later.'
		});
	}
	const result = await response.json();
	// Map them to proper JS casing. no snakes here
	availableTrees = result.map((tree: TreeOption) => ({
		id: tree.id,
		commonName: tree.common_name,
		scientificName: tree.scientific_name
	}));

	const form = await superValidate(zod(schema));
	return {
		user: locals.user,
		form,
		availableTrees
	};
};

export const actions: Actions = {
	default: async ({ request, locals }) => {
		if (!locals.user) {
			return fail(401, { message: 'Authentication required.' });
		}
		const userId = locals.user.id;

		const form = await superValidate(request, zod(schema));
		if (!form.valid) {
			return fail(400, { form });
		}

		console.log(userId);

		const apiUrl = `${API_ROUTE}/tree-request`;
		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				tree_id: form.data.treeId,
				resident_id: userId,
				site_description: form.data.siteDescription
			})
		});
		if (!response.ok) {
			const errorBody = await response.text();
			console.error(`API Error (${response.status}): ${errorBody}`);
			return message(form, 'Failed to submit request due to a server error (API).', {
				status: 500
			});
		}

		throw redirect(303, '/dashboard');
	}
};
