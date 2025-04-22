import jwt from 'jsonwebtoken';
import { JWT_SECRET } from '$env/static/private';
import argon2 from 'argon2';
import type { Cookies } from '@sveltejs/kit';

export const signJWT = (payload: object, cookies: Cookies) => {
	const token = jwt.sign(payload, JWT_SECRET, {
		expiresIn: '7d'
	});
	// Success!
	cookies.set('auth_token', token, {
		path: '/',
		httpOnly: true,
		secure: process.env.NODE_ENV === 'production',
		maxAge: 60 * 60 * 24 * 7, // 7 days
		sameSite: 'lax'
	});
};

export const hashPassword = async (password: string) => {
	if (process.env.HASH_PASSWORDS) {
		return await argon2.hash(password);
	}
	return password;
};

export const verifyPassword = async (password: string, hashedPassword: string) => {
	if (process.env.HASH_PASSWORDS) {
		return await argon2.verify(password, hashedPassword);
	}
	return password == hashedPassword;
};
