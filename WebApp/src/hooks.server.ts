import type { Handle } from '@sveltejs/kit';
import jwt from 'jsonwebtoken';
import { JWT_SECRET } from '$env/static/private'; // Import the secret

export const handle: Handle = async ({ event, resolve }) => {
	const token = event.cookies.get('auth_token');
	event.locals.user = null;
	if (token) {
		try {
			const userData = verifyAuthToken(token);
			if (userData) {
				event.locals.user = userData;
			} else {
				console.log('Invalid token found, clearing cookie.');
				event.cookies.delete('auth_token', { path: '/' });
			}
		} catch (error) {
			console.error('Error during token verification process:', error);
			event.cookies.delete('auth_token', { path: '/' });
		}
	}
	const response = await resolve(event);
	return response;
};

function verifyAuthToken(token: string): App.Locals['user'] | null {
	try {
		const decoded = jwt.verify(token, JWT_SECRET);
		// Typescript gymnastics
		if (
			typeof decoded === 'object' &&
			decoded !== null &&
			'userId' in decoded &&
			'email' in decoded &&
			'firstName' in decoded &&
			'lastName' in decoded &&
			'street' in decoded &&
			'zipCode' in decoded &&
			'neighborhood' in decoded &&
			'isVolunteer' in decoded
		) {
			return {
				id: decoded.userId,
				email: decoded.email,
				firstName: decoded.firstName,
				lastName: decoded.lastName,
				street: decoded.street,
				zipCode: decoded.zipCode,
				neighborhood: decoded.neighborhood,
				isVolunteer: Boolean(decoded.isVolunteer)
			};
		}

		// Payload structure doesn't match expected user data
		console.warn('Decoded JWT payload does not match expected user structure:', decoded);
		return null;
	} catch (error) {
		console.error('JWT verification failed: ', error);
		return null;
	}
}
