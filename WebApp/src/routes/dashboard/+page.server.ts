import { API_ROUTE } from '$lib/constants';
import type { PageServerLoad } from './$types';
import { error, redirect, type Actions } from '@sveltejs/kit';

interface ApiTreeRequest {
	id: number;
	submission_timestamp: string;
	approved: boolean;
}

export const load: PageServerLoad = async ({ locals, fetch }) => {
	if (!locals.user) {
		throw redirect(302, '/login');
	}
	// Fetch all tree requests based on user id
	let treeRequests: ApiTreeRequest[] = [];
	const apiUrl = `${API_ROUTE}/tree-requests?resident_id=${encodeURIComponent(locals.user.id)}`;
	const response = await fetch(apiUrl);

	if (!response.ok) {
		const errorBody = await response.text();
		console.error(`API Error (${response.status}): ${errorBody}`);
		error(500, {
			message: 'Failed. Please try again later.'
		});
	}

	treeRequests = await response.json();
	console.log('Successfully fetched tree requests:', treeRequests);
	return {
		user: locals.user,
		treeRequests: treeRequests
	};
};

export const actions: Actions = {
	logout: async ({ cookies }) => {
		cookies.delete('auth_token', { path: '/' });
		console.log('User logged out, cookie cleared.');
		throw redirect(303, '/login');
	}
};
