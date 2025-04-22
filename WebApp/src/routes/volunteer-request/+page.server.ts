import { z } from 'zod';
import { superValidate, message } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { API_ROUTE } from '$lib/constants';

const schema = z.object({
	notes: z.string().max(1000, 'Notes must be 1000 characters or less.').optional()
});

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.user) {
		throw redirect(302, '/login');
	}
	const form = await superValidate(zod(schema));
	return { form, user: locals.user };
};

export const actions: Actions = {
	default: async ({ request, locals, fetch }) => {
		if (!locals.user) {
			throw redirect(302, '/login');
		}

		const form = await superValidate(request, zod(schema));
		if (!form.valid) {
			return fail(400, { form });
		}

		const notes = form.data.notes || '';
		const apiUrl = `${API_ROUTE}/volunteer-requests`;

		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ user_id: locals.user.id, notes: notes })
		});
		if (!response.ok) {
			const errorData = await response.json().catch(() => ({ error: 'API error' }));
			return message(form, `Failed to submit request: ${errorData.error}`, {
				status: 500
			});
		}
		return message(form, 'Thank you for expressing interest in volunteering!');
	}
};
