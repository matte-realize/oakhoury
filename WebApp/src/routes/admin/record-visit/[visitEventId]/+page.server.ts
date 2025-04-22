import { API_ROUTE } from '$lib/constants';
import { error, fail, redirect } from '@sveltejs/kit';
import { message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';
import type { Actions, PageServerLoad } from './$types';

const recordVisitSchema = z.object({
	observations: z.string().optional(),
	photo_library_link: z.string().url().optional().or(z.literal('')),
	additional_visit_required: z.boolean().default(false)
});

export const load: PageServerLoad = async ({ locals, params, fetch }) => {
	if (!locals.user) {
		throw redirect(302, '/login');
	}
	const isMemberApiUrl = `${API_ROUTE}/is_organization_member?user_id=${encodeURIComponent(locals.user.id)}`;
	const isMemberResponse = await fetch(isMemberApiUrl);
	if (!isMemberResponse.ok) throw new Error('Failed permission check');
	const { is_organization_member } = await isMemberResponse.json();
	if (!is_organization_member) throw redirect(302, '/dashboard');

	const { visitEventId } = params;
	if (!visitEventId || isNaN(parseInt(visitEventId))) {
		throw error(400, 'Invalid Visit Event ID.');
	}
	const eventIdNum = parseInt(visitEventId);

	let treeRequestId: number | null = null;
	const visitDetailsRes = await fetch(`${API_ROUTE}/visit-details/${eventIdNum}`);
	if (visitDetailsRes.ok) {
		const visitDetails = await visitDetailsRes.json();
		treeRequestId = visitDetails.tree_request_id;
	} else {
		console.error(`Failed to fetch details for visit ${eventIdNum}: ${visitDetailsRes.status}`);
		if (visitDetailsRes.status === 404) {
			throw error(404, 'Visit event not found.');
		}
		throw error(500, 'Failed to load necessary visit details.');
	}

	if (treeRequestId === null) {
		throw error(500, 'Could not determine the associated tree request.');
	}

	const form = await superValidate(zod(recordVisitSchema));

	return { form, visitEventId: eventIdNum, treeRequestId };
};

export const actions: Actions = {
	default: async ({ request, fetch, params, locals }) => {
		if (!locals.user) throw error(401, 'Not authenticated');

		const form = await superValidate(request, zod(recordVisitSchema));
		const { visitEventId } = params;

		if (!form.valid) {
			return fail(400, { form });
		}

		if (!visitEventId || isNaN(parseInt(visitEventId))) {
			return message(form, 'Invalid Visit Event ID.', { status: 400 });
		}
		const eventIdNum = parseInt(visitEventId);

		const apiUrl = `${API_ROUTE}/visit-events`;

		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				scheduled_visit_id: eventIdNum,
				observations: form.data.observations,
				photo_library_link: form.data.photo_library_link,
				additional_visit_required: form.data.additional_visit_required
			})
		});

		if (!response.ok) {
			const errorBody = await response.text();
			console.error(`API Error (${response.status}) recording visit event: ${errorBody}`);
			const errorMessage = `Failed to record visit outcome. Server responded: ${response.statusText}`;
			return message(form, errorMessage, { status: 500 });
		}

		const visitDetailsRes = await fetch(`${API_ROUTE}/visit-details/${eventIdNum}`);
		if (visitDetailsRes.ok) {
			const visitDetails = await visitDetailsRes.json();
			const treeRequestId = visitDetails.tree_request_id;
			if (treeRequestId) {
				throw redirect(303, `/admin/details/${treeRequestId}`);
			}
		}
		throw redirect(303, '/admin');
	}
};
