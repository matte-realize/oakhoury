import { API_ROUTE } from '$lib/constants';
import { error, fail, redirect } from '@sveltejs/kit';
import { message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';
import type { Actions, PageServerLoad } from './$types';

const schema = z.object({
	event_timestamp: z.string().refine((val) => !isNaN(Date.parse(val)), {
		message: 'Invalid date and time format'
	}),
	notes: z.string().optional()
});

export const load: PageServerLoad = async ({ locals, params }) => {
	if (!locals.user) {
		throw redirect(302, '/login');
	}
	const isMemberApiUrl = `${API_ROUTE}/is_organization_member?user_id=${encodeURIComponent(locals.user.id)}`;
	try {
		const isMemberResponse = await fetch(isMemberApiUrl);
		if (!isMemberResponse.ok) throw new Error('Failed permission check');
		const { is_organization_member } = await isMemberResponse.json();
		if (!is_organization_member) throw redirect(302, '/dashboard');
	} catch (err) {
		console.error('Auth check failed:', err);
		throw error(500, 'Failed to verify permissions.');
	}

	// Validate treeRequestId
	const { treeRequestId } = params;
	if (!treeRequestId || isNaN(parseInt(treeRequestId))) {
		throw error(400, 'Invalid Tree Request ID.');
	}

	const form = await superValidate(zod(schema));

	return { form, treeRequestId };
};

export const actions: Actions = {
	default: async ({ request, fetch, params }) => {
		const form = await superValidate(request, zod(schema));
		const { treeRequestId } = params;

		if (!form.valid) {
			return fail(400, { form });
		}

		if (!treeRequestId || isNaN(parseInt(treeRequestId))) {
			return message(form, 'Invalid Tree Request ID.', { status: 400 });
		}

		const apiUrl = `${API_ROUTE}/schedule-planting`;

		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				tree_request_id: parseInt(treeRequestId),
				timestamp: new Date(form.data.event_timestamp).toISOString(),
				notes: form.data.notes
			})
		});

		if (!response.ok) {
			const errorBody = await response.text();
			console.error(`API Error (${response.status}) scheduling planting: ${errorBody}`);
			return message(
				form,
				`Failed to schedule planting. Server responded: ${response.statusText}`,
				{
					status: 500
				}
			);
		}

		throw redirect(303, `/admin/details/${treeRequestId}`);
	}
};
