// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		type PermitStatus = 'pending' | 'approved' | 'denied';

		type TreeRequestStatus =
			| 'completed'
			| 'waiting for planting'
			| 'waiting for visit'
			| 'needs permit'
			| 'pending approval'
			| 'denied';

		interface TreeRequest {
			id: number;
			resident_id: number;
			submission_timestamp: Date;
			tree_id: number;
			site_description: string;
			approved: boolean;
		}

		interface Locals {
			user: {
				id: string;
				email: string;
				firstName: string;
				lastName: string;
				street: string;
				zipCode: string;
				neighborhood: string;
				isVolunteer: boolean;
			} | null;
		}
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
