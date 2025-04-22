import { z } from 'zod';
import { message, superValidate } from 'sveltekit-superforms/server';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { zod } from 'sveltekit-superforms/adapters';
import { signJWT, verifyPassword } from '$lib/utils';
import { API_ROUTE } from '$lib/constants';

interface APIUser {
	id: number;
	password: string;
	first_name: string;
	last_name: string;
	is_volunteer: boolean;
	street: string;
	zip_code: string;
	neighborhood: string;
}

const schema = z.object({
	email: z.string().email('Please enter a valid email address.'),
	password: z.string().nonempty('Password cannot be empty.')
});

export const load: PageServerLoad = async ({ locals }) => {
	if (locals.user) {
		throw redirect(302, '/dashboard');
	}
	const form = await superValidate(zod(schema));
	return { form };
};

export const actions: Actions = {
	default: async ({ request, cookies, fetch }) => {
		const form = await superValidate(request, zod(schema));
		if (!form.valid) {
			return fail(400, { form });
		}

		const apiUrl = `${API_ROUTE}/login`;
		// This will return the hashed password. We compare here.
		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				email: form.data.email
			})
		});

		if (response.status === 404) {
			return message(form, 'Invalid email or password.', {
				status: 401
			});
		}

		if (!response.ok) {
			const errorBody = await response.text();
			console.error(`API Error (${response.status}): ${errorBody}`);
			return message(form, 'API error.', {
				status: 500
			});
		}
		const user: APIUser = await response.json();

		const validPassword = user && (await verifyPassword(user.password, form.data.password));
		if (!validPassword) {
			console.error('Invalid login attempt for email:', form.data.email);
			// Return same error message because this is more secure :) (they don't know that this is a valid email)
			return message(form, 'Invalid email or password.', {
				status: 401
			});
		}
		// Credentials are correct, generate JWT
		const payload = {
			userId: user.id,
			email: form.data.email,
			firstName: user.first_name,
			lastName: user.last_name,
			isVolunteer: user.is_volunteer,
			street: user.street,
			zipCode: user.zip_code,
			neighborhood: user.neighborhood
		};

		try {
			signJWT(payload, cookies);
		} catch (err) {
			console.error('JWT Signing Error: ', err);
			return message(form, 'Login failed due to a server error. Please try again.', {
				status: 500
			});
		}
		throw redirect(303, '/dashboard');
	}
};
