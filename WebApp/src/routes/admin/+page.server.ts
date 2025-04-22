import { API_ROUTE } from '$lib/constants';
import { z } from 'zod';
import type { PageServerLoad } from './$types';
import { error, redirect, type Actions, fail } from '@sveltejs/kit';
import { message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';

const schema = z.object({
	requestId: z.coerce.number().int().positive()
});

export const load: PageServerLoad = async ({ locals, fetch }) => {
	if (!locals.user) {
		throw redirect(302, '/login');
	}
	// Check if user is organizaiton_member
	// Not vulnerable to MITM attack since this runs on the server
	const apiUrl = `${API_ROUTE}/is_organization_member?user_id=${encodeURIComponent(locals.user.id)}`;
	const response = await fetch(apiUrl);
	if (!response.ok) {
		const errorBody = await response.text();
		console.error(`API Error (${response.status}): ${errorBody}`);
		throw error(500, {
			message: 'Failed to check organization membership. Please try again later.'
		});
	}
	const { is_organization_member } = await response.json();
	if (!is_organization_member) {
		throw redirect(302, '/dashboard');
	}

	// Fetch all tree requests
	const apiUrlTreeRequests = `${API_ROUTE}/all-tree-requests`;
	const responseTreeRequests = await fetch(apiUrlTreeRequests);
	if (!responseTreeRequests.ok) {
		const errorBody = await responseTreeRequests.text();
		console.error(`API Error (${responseTreeRequests.status}): ${errorBody}`);
		throw error(500, {
			message: 'Failed to fetch tree requests. Please try again later.'
		});
	}
	const tree_requests = await responseTreeRequests.json();
	console.log('Successfully fetched tree requests:', tree_requests);

	const form = await superValidate(zod(schema));

	return {
		user: locals.user,
		treeRequests: tree_requests,
		form
	};
};

export const actions: Actions = {
	approveRequest: async ({ request, fetch }) => {
		const form = await superValidate(request, zod(schema));
		if (!form.valid) {
			return fail(400, { form });
		}

		const requestId = form.data.requestId;
		const apiUrl = `${API_ROUTE}/accept-tree-request`;

		const response = await fetch(apiUrl, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ tree_request_id: requestId })
		});

		if (!response.ok) {
			const errorBody = await response.text();
			console.error(`API Error (${response.status}) approving request ${requestId}: ${errorBody}`);
			return message(form, 'Failed to approve request. API error.', { status: 500 });
		}
		return message(form, 'Request approved successfully!');
	},
	denyRequest: async ({ request, fetch }) => {
		const form = await superValidate(request, zod(schema));
		if (!form.valid) {
			return fail(400, { form });
		}

		const requestId = form.data.requestId;
		const apiUrl = `${API_ROUTE}/deny-tree-request`;

		const response = await fetch(apiUrl, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ tree_request_id: requestId })
		});
		if (!response.ok) {
			const errorBody = await response.text();
			console.error(`API Error (${response.status}) denying request ${requestId}: ${errorBody}`);
			return message(form, 'Failed to deny request. API error.', { status: 500 });
		}
		return message(form, 'Request denied successfully!');
	}
};
