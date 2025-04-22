import { error, fail, redirect } from '@sveltejs/kit';
import { superValidate, message } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';
import { hashPassword, signJWT } from '$lib/utils';
import { API_ROUTE } from '$lib/constants';

const POSTGRESQL_UNIQUE_VIOLATION = '23505';
const schema = z.object({
	firstName: z.string().nonempty().max(50),
	lastName: z.string().nonempty().max(50),
	email: z.string().email().nonempty().max(100),
	password: z.string().min(8).max(50),
	street: z.string().nonempty().max(50),
	zipCode: z.string().regex(/^\d{5}$/, 'ZIP code must contain exactly 5 digits'),
	neighborhood: z.string().nonempty().max(100)
});

export const load = async ({ locals }) => {
	if (locals.user) {
		throw redirect(302, '/dashboard');
	}
	const form = await superValidate(zod(schema));
	// Load available neighborhoods for the dropdown
	const apiUrl = `${API_ROUTE}/neighborhoods`;
	const response = await fetch(apiUrl);
	if (!response.ok) {
		const errorBody = await response.text();
		console.error(`API Error (${response.status}): ${errorBody}`);
		throw error(500, {
			message: 'Failed to load tree types. Please try again later.'
		});
	}
	const neighborhoods = await response.json();
	return { form, neighborhoods };
};

export const actions = {
	default: async ({ request, cookies }) => {
		const form = await superValidate(request, zod(schema));
		if (!form.valid) {
			return fail(400, { form });
		}

		const hashedPassword = await hashPassword(form.data.password);
		// Register the user in the database
		const apiUrl = `${API_ROUTE}/register`;
		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				email: form.data.email,
				password: hashedPassword,
				first_name: form.data.firstName,
				last_name: form.data.lastName,
				street: form.data.street,
				zip_code: form.data.zipCode,
				neighborhood: form.data.neighborhood
			})
		});
		if (!response.ok) {
			const errorData = await response.json();
			if (errorData && errorData.error === POSTGRESQL_UNIQUE_VIOLATION) {
				form.errors.email = ['This email address is already registered.'];
				return fail(400, { form });
			}
			// Handle other API errors (hopefully not)
			console.error('API Registration Error:', response.status, errorData);
			return message(form, `Registration failed: ${errorData.message || 'API error'}`, {
				status: 500
			});
		}
		const result = await response.json();

		console.log('User registered successfully via API:', result);
		const payload = {
			userId: result.id,
			email: form.data.email,
			firstName: form.data.firstName,
			lastName: form.data.lastName,
			isVolunteer: false,
			street: form.data.street,
			zipCode: form.data.zipCode,
			neighborhood: form.data.neighborhood
		};
		try {
			signJWT(payload, cookies);
		} catch (err) {
			console.error('JWT Signing Error: ', err);
			return message(form, 'Login failed due to a server error. Please try again.', {
				status: 500
			});
		}
		redirect(303, '/dashboard');
	}
};
