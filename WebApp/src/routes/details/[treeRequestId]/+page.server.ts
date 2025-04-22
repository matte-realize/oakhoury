import { z } from 'zod';
import { API_ROUTE } from '$lib/constants';
import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { fail, message, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';

interface ApiTreeRequestDetails {
	common_name: string;
	scientific_name: string;
	status: string;
	days_since_planting: number;
	permit_status: App.PermitStatus;
}

const schema = z.object({
	status: z.enum(['pending', 'approved', 'denied'], {
		errorMap: () => ({ message: 'Invalid status' })
	})
});

export const load: PageServerLoad = async ({ locals, params, fetch }) => {
	if (!locals.user) {
		throw redirect(302, '/login');
	}
	// Get tree status from params
	const treeRequestId = params.treeRequestId;
	const apiUrl = `${API_ROUTE}/details?resident_id=${encodeURIComponent(locals.user.id)}&tree_request_id=${encodeURIComponent(treeRequestId)}`;
	const response = await fetch(apiUrl);

	if (!response.ok) {
		const errorBody = await response.text();
		console.error(`API Error (${response.status}): ${errorBody}`);
		error(500, {
			message: 'Failed. Please try again later.'
		});
	}
	const details: ApiTreeRequestDetails = await response.json();
	console.log('Successfully fetched tree request details:', details);

	const form = await superValidate(zod(schema));
	return {
		form,
		commonName: details.common_name,
		scientificName: details.scientific_name,
		status: details.status,
		daysSincePlanting: details.days_since_planting,
		permitStatus: details.permit_status
	};
};

// Handle being able to set new status of permit
// CREATE TYPE status AS ENUM ('pending', 'approved', 'denied');
export const actions = {
	default: async ({ locals, params, request, fetch }) => {
		if (!locals.user) {
			throw redirect(302, '/login');
		}

		const form = await superValidate(request, zod(schema));
		const { status } = form.data;
		if (!form.valid) {
			return fail(400, { form });
		}

		const treeRequestId = params.treeRequestId;

		const apiUrl = `${API_ROUTE}/update-permit-status`;
		const response = await fetch(apiUrl, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				status: status,
				tree_request_id: treeRequestId
			})
		});

		if (!response.ok) {
			const errorBody = await response.text();
			console.error(`API Error (${response.status}): ${errorBody}`);
			return message(form, 'API error.', {
				status: 500
			});
		}

		return { form };
	}
};
