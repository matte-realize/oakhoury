import { API_ROUTE } from '$lib/constants';
import { error, fail, redirect } from '@sveltejs/kit';
import { message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';
import type { Actions, PageServerLoad } from './$types';

const assignVolunteerSchema = z.object({
	volunteerId: z.coerce.number().int().positive('Please select a volunteer.')
});

const assignOrgMemberSchema = z.object({
	orgMemberId: z.coerce.number().int().positive('Please select an organization member.')
});

const recordOutcomeSchema = z.object({
	successful: z.boolean({ required_error: 'Please indicate if the planting was successful.' }),
	observations: z.string().optional(),
	attended_volunteer_ids: z.array(z.coerce.number().int().positive()).optional().default([])
});

export const load: PageServerLoad = async ({ locals, fetch, params }) => {
	if (!locals.user) {
		throw redirect(302, '/login');
	}
	const isMemberApiUrl = `${API_ROUTE}/is_organization_member?user_id=${encodeURIComponent(locals.user.id)}`;
	const isMemberResponse = await fetch(isMemberApiUrl);
	if (!isMemberResponse.ok) throw new Error('Failed permission check');
	const { is_organization_member } = await isMemberResponse.json();
	if (!is_organization_member) throw redirect(302, '/dashboard');

	const { plantingEventId } = params;
	if (!plantingEventId || isNaN(parseInt(plantingEventId))) {
		throw error(400, 'Invalid Planting Event ID.');
	}
	const eventIdNum = parseInt(plantingEventId);

	const [detailsRes, volunteersRes, membersRes] = await Promise.all([
		fetch(`${API_ROUTE}/scheduled-planting-details/${eventIdNum}`),
		fetch(`${API_ROUTE}/available-volunteers`),
		fetch(`${API_ROUTE}/available-org-members`)
	]);

	if (!detailsRes.ok) {
		if (detailsRes.status === 404) throw error(404, 'Planting event not found.');
		throw error(detailsRes.status, 'Failed to load planting details.');
	}
	if (!volunteersRes.ok) throw error(volunteersRes.status, 'Failed to load available volunteers.');
	if (!membersRes.ok)
		throw error(membersRes.status, 'Failed to load available organization members.');

	const plantingDetails = await detailsRes.json();
	const availableVolunteers = await volunteersRes.json();
	const availableOrgMembers = await membersRes.json();

	const assignVolunteerForm = await superValidate(zod(assignVolunteerSchema), {
		id: 'assignVolunteerForm'
	});
	const assignOrgMemberForm = await superValidate(zod(assignOrgMemberSchema), {
		id: 'assignOrgMemberForm'
	});
	const recordOutcomeForm = await superValidate(zod(recordOutcomeSchema), {
		id: 'recordOutcomeForm'
	});

	return {
		plantingDetails,
		availableVolunteers,
		availableOrgMembers,
		assignVolunteerForm,
		assignOrgMemberForm,
		recordOutcomeForm,
		plantingEventId: eventIdNum
	};
};

export const actions: Actions = {
	assignVolunteer: async ({ request, fetch, params }) => {
		const form = await superValidate(request, zod(assignVolunteerSchema), {
			id: 'assignVolunteerForm'
		});
		const { plantingEventId } = params;

		if (!form.valid) return fail(400, { form });
		if (!plantingEventId) return message(form, 'Missing planting event ID.', { status: 400 });

		const apiUrl = `${API_ROUTE}/add-volunteer-to-planting`;
		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				planting_event_id: parseInt(plantingEventId),
				volunteer_id: form.data.volunteerId
			})
		});
		if (!response.ok) {
			const errorBody = await response.text();
			return message(form, `Failed to assign volunteer: ${errorBody}`, {
				status: 500
			});
		}
		return message(form, 'Volunteer assigned successfully!');
	},

	assignOrgMember: async ({ request, fetch, params }) => {
		const form = await superValidate(request, zod(assignOrgMemberSchema), {
			id: 'assignOrgMemberForm'
		});
		const { plantingEventId } = params;

		if (!form.valid) return fail(400, { form });
		if (!plantingEventId) return message(form, 'Missing planting event ID.', { status: 400 });

		const apiUrl = `${API_ROUTE}/add-org-member-to-planting`;
		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				scheduled_planting_id: parseInt(plantingEventId),
				organization_member_id: form.data.orgMemberId
			})
		});
		if (!response.ok) {
			const errorBody = await response.text();
			return message(form, `Failed to assign org member: ${errorBody}`, {
				status: 500
			});
		}
		return message(form, 'Organization member assigned successfully!');
	},

	cancelPlanting: async ({ fetch, params }) => {
		const { plantingEventId } = params;
		if (!plantingEventId) return fail(400, { message: 'Missing planting event ID.' });

		const apiUrl = `${API_ROUTE}/cancel-planting/${plantingEventId}`;
		const response = await fetch(apiUrl, { method: 'PATCH' });
		if (!response.ok) {
			const errorBody = await response.text();
			return fail(response.status, { message: `Failed to cancel planting: ${errorBody}` });
		}
		return { success: true, message: 'Planting cancelled successfully!' };
	},

	recordOutcome: async ({ request, fetch, params }) => {
		const form = await superValidate(request, zod(recordOutcomeSchema), {
			id: 'recordOutcomeForm'
		});
		const { plantingEventId } = params;

		if (!form.valid) {
			console.error('Form validation failed:', form.errors);
			return fail(400, { form });
		}
		if (!plantingEventId || isNaN(parseInt(plantingEventId))) {
			return message(form, 'Invalid Planting Event ID.', { status: 400 });
		}
		const eventIdNum = parseInt(plantingEventId);

		const outcomeApiUrl = `${API_ROUTE}/new-planting-event`;
		const outcomeResponse = await fetch(outcomeApiUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				scheduled_planting_id: eventIdNum,
				successful: form.data.successful,
				observations: form.data.observations
			})
		});

		if (!outcomeResponse.ok) {
			const errorBody = await outcomeResponse.text();
			console.error(
				`API Error (${outcomeResponse.status}) recording planting outcome: ${errorBody}`
			);
			let errorMessage = `Failed to record planting outcome. Server responded: ${outcomeResponse.statusText}`;
			errorMessage = JSON.parse(errorBody).error || errorMessage;

			return message(form, errorMessage, { status: 500 });
		}

		const attendedVolunteerIds = form.data.attended_volunteer_ids || [];
		const volunteerAttendApiUrl = `${API_ROUTE}/add-volunteer-to-planting-event`;

		const volunteerPromises = attendedVolunteerIds.map((volunteerId) =>
			fetch(volunteerAttendApiUrl, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					planting_event_id: eventIdNum,
					volunteer_id: volunteerId
				})
			}).then((res) => {
				if (!res.ok) {
					console.error(`Failed to record attendance for volunteer ${volunteerId}: ${res.status}`);
				}
				return res.ok;
			})
		);

		await Promise.all(volunteerPromises);
		const detailsRes = await fetch(`${API_ROUTE}/scheduled-planting-details/${eventIdNum}`);
		if (detailsRes.ok) {
			const details = await detailsRes.json();
			if (details.tree_request_id) {
				throw redirect(303, `/admin/details/${details.tree_request_id}`);
			}
		}
		// Fallback redirect
		throw redirect(303, '/admin');
	}
};
