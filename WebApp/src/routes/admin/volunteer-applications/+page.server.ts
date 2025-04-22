import { API_ROUTE } from '$lib/constants';
import { error, fail, redirect } from '@sveltejs/kit';
import { message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';
import type { Actions, PageServerLoad } from './$types';

const schema = z.object({
	residentId: z.coerce.number().int().positive()
});

export const load: PageServerLoad = async ({ locals, fetch }) => {
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

	// Fetch pending applications
	let pendingApplications = [];
	const apiUrl = `${API_ROUTE}/pending-volunteer-applications`;
	const response = await fetch(apiUrl);
	if (!response.ok) {
		console.error(`API Error (${response.status}) fetching pending apps: ${await response.text()}`);
		throw error(500, 'Failed to load pending volunteer applications.');
	}
	pendingApplications = await response.json();

	const form = await superValidate(zod(schema));

	return { form, pendingApplications };
};

export const actions: Actions = {
	approveVolunteer: async ({ request, fetch }) => {
		const form = await superValidate(request, zod(schema));
		console.log(form);
		if (!form.valid) {
			return fail(400, { form });
		}

		const { residentId } = form.data;
		const apiUrl = `${API_ROUTE}/approve-volunteer`;

		const response = await fetch(apiUrl, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				resident_id: residentId
			})
		});

		if (!response.ok) {
			const errorBody = await response.text();
			console.error(`API Error (${response.status}) approving volunteer: ${errorBody}`);
			return message(
				form,
				`Failed to approve volunteer. Server responded: ${response.statusText}`,
				{
					status: 500
				}
			);
		}

		return message(form, 'Volunteer approved successfully!');
	}
};
