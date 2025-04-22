import { API_ROUTE } from '$lib/constants';
import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, fetch, params }) => {
	if (!locals.user) {
		throw redirect(302, '/login');
	}
	// Check if user is org member
	const isMemberApiUrl = `${API_ROUTE}/is_organization_member?user_id=${encodeURIComponent(locals.user.id)}`;
	const isMemberResponse = await fetch(isMemberApiUrl);
	if (!isMemberResponse.ok) {
		console.error(`API Error (${isMemberResponse.status}): ${await isMemberResponse.text()}`);
		throw error(500, 'Failed to verify user permissions.');
	}
	const { is_organization_member } = await isMemberResponse.json();
	if (!is_organization_member) {
		throw redirect(302, '/dashboard');
	}

	// Get admin detials
	const { treeRequestId } = params;
	if (!treeRequestId || isNaN(parseInt(treeRequestId))) {
		throw error(400, 'Invalid Tree Request ID provided.');
	}
	const detailsApiUrl = `${API_ROUTE}/tree-request-details-admin?tree_request_id=${encodeURIComponent(treeRequestId)}`;
	const response = await fetch(detailsApiUrl);
	if (!response.ok) {
		if (response.status === 404) {
			throw error(404, 'Tree request not found.');
		}
		const errorBody = await response.text();
		console.error(
			`API Error (${response.status}) fetching details for ${treeRequestId}: ${errorBody}`
		);
		throw error(response.status, 'Failed to fetch tree request details.');
	}

	const data = await response.json();
	return {
		requestDetails: {
			tree_common_name: data.tree_common_name,
			tree_scientific_name: data.tree_scientific_name,
			tree_inventory: data.tree_inventory,
			site_description: data.site_description,
			resident_street: data.resident_street,
			resident_zip_code: data.resident_zip_code,
			resident_neighborhood: data.resident_neighborhood,
			status: data.status
		},
		scheduledVisits: data.scheduled_visits || [],
		scheduledPlantings: data.scheduled_plantings || []
	};
};
