/**
 * API Client for Church Agenda
 * Handles all API requests with envelope parsing and auth token injection
 */

export interface ApiResponse<T = any> {
    ok: boolean;
    data: T | null;
    error_key: string | null;
}

class ApiClient {
    private baseUrl: string;

    constructor() {
        this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    }

    private getToken(): string | null {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem('auth_token');
    }

    async request<T = any>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<ApiResponse<T>> {
        const token = this.getToken();

        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...(typeof options.headers === 'object' && options.headers !== null 
                ? Object.fromEntries(Object.entries(options.headers as Record<string, string>))
                : {}),
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers,
            });

            const data: ApiResponse<T> = await response.json();
            return data;
        } catch (error) {
            return {
                ok: false,
                data: null,
                error_key: 'internal_error',
            };
        }
    }

    // Auth endpoints
    async login(email: string, password: string, organization_slug?: string) {
        const body: any = { email, password };
        if (organization_slug) body.organization_slug = organization_slug;
        return this.request<{ token: string; user_id: number; role: string }>('/auth/login', {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    async register(email: string, password: string, full_name: string, organization_slug?: string) {
        const body: any = { email, password, full_name };
        if (organization_slug) body.organization_slug = organization_slug;
        return this.request<{ user_id: number; message: string }>('/auth/register', {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    async approve(email: string) {
        return this.request<{ message: string }>('/auth/approve', {
            method: 'POST',
            body: JSON.stringify({ email }),
        });
    }

    // Members endpoints
    async getDirectory(params: { search?: string; limit?: number; offset?: number } = {}) {
        const query = new URLSearchParams();
        if (params.search) query.set('search', params.search);
        if (params.limit) query.set('limit', params.limit.toString());
        if (params.offset) query.set('offset', params.offset.toString());

        return this.request<{ results: any[]; page: number; limit: number; offset: number }>(
            `/members/directory?${query.toString()}`
        );
    }

    async updateProfile(updates: any) {
        return this.request<{ message: string }>('/members/me', {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
    }

    // Events endpoints
    async listEvents(params: { from?: string; to?: string } = {}) {
        const query = new URLSearchParams();
        if (params.from) query.set('from', params.from);
        if (params.to) query.set('to', params.to);

        // Include selected organization slug from localStorage when available
        if (typeof window !== 'undefined') {
            const orgSlug = localStorage.getItem('selected_church_slug');
            if (orgSlug) query.set('organization', orgSlug);
        }

        const queryString = query.toString();
        return this.request<{ results: any[] }>(
            `/events${queryString ? `?${queryString}` : ''}`
        );
    }

    async createEvent(event: any) {
        return this.request<{ event_id: number; message: string }>('/events', {
            method: 'POST',
            body: JSON.stringify(event),
        });
    }

    async rsvpEvent(eventId: number, status: string) {
        return this.request<{ message: string }>(`/events/${eventId}/rsvp`, {
            method: 'POST',
            body: JSON.stringify({ status }),
        });
    }

    // Announcements endpoints
    async getAnnouncementsFeed(params: { limit?: number; offset?: number } = {}) {
        const query = new URLSearchParams();
        if (params.limit) query.set('limit', params.limit.toString());
        if (params.offset) query.set('offset', params.offset.toString());

        // Include selected organization slug from localStorage when available
        if (typeof window !== 'undefined') {
            const orgSlug = localStorage.getItem('selected_church_slug');
            if (orgSlug) query.set('organization', orgSlug);
        }

        return this.request<{ results: any[]; limit: number; offset: number }>(
            `/announcements/feed?${query.toString()}`
        );
    }

    async postAnnouncement(announcement: any) {
        return this.request<{ announcement_id: number; message: string }>('/announcements', {
            method: 'POST',
            body: JSON.stringify(announcement),
        });
    }

    // Worship Files endpoints
    async uploadFile(file: File) {
        const formData = new FormData();
        formData.append('file', file);

        const token = this.getToken();
        const headers: HeadersInit = {};
        if (token) {
            (headers as any)['Authorization'] = `Bearer ${token}`;
        }

        return fetch(`${this.baseUrl}/worship/files/upload`, {
            method: 'POST',
            headers,
            body: formData,
        }).then(res => res.json());
    }

    async downloadFile(assetId: number) {
        const token = this.getToken();
        const headers: HeadersInit = {};
        if (token) {
            (headers as any)['Authorization'] = `Bearer ${token}`;
        }

        return fetch(`${this.baseUrl}/worship/files/${assetId}/download`, {
            headers,
        });
    }

    async deleteFile(assetId: number) {
        return this.request<{ message: string }>(`/worship/files/${assetId}`, {
            method: 'DELETE',
        });
    }

    // Worship Repertoire endpoints
    async listSongs(params: { search?: string; limit?: number; offset?: number } = {}) {
        const query = new URLSearchParams();
        if (params.search) query.set('search', params.search);
        if (params.limit) query.set('limit', params.limit.toString());
        if (params.offset) query.set('offset', params.offset.toString());

        return this.request<{ results: any[]; limit: number; offset: number }>(
            `/worship/repertoire/songs?${query.toString()}`
        );
    }

    // Bible integration
    async getPassage(ref: string, translation?: string) {
        const query = new URLSearchParams();
        query.set('ref', ref);
        if (translation) query.set('translation', translation);
        return this.request<any>(`/bible/passage?${query.toString()}`);
    }

    async createSong(song: { title: string; artist?: string; bpm?: number; default_key?: string }) {
        return this.request<{ song_id: number; message: string }>('/worship/repertoire/songs', {
            method: 'POST',
            body: JSON.stringify(song),
        });
    }

    async updateSong(songId: number, updates: any) {
        return this.request<{ message: string }>(`/worship/repertoire/songs/${songId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
    }

    async addSongAsset(songId: number, asset: { type: string; url?: string; asset_id?: number; label?: string; instrument_tag_ids?: string[] }) {
        return this.request<{ song_asset_id: number; message: string }>(`/worship/repertoire/songs/${songId}/assets`, {
            method: 'POST',
            body: JSON.stringify(asset),
        });
    }

    async removeSongAsset(songAssetId: number) {
        return this.request<{ message: string }>(`/worship/repertoire/song-assets/${songAssetId}`, {
            method: 'DELETE',
        });
    }

    // Worship Schedule endpoints
    async listPlans(params: { from_date?: string; to_date?: string } = {}) {
        const query = new URLSearchParams();
        if (params.from_date) query.set('from_date', params.from_date);
        if (params.to_date) query.set('to_date', params.to_date);

        const queryString = query.toString();
        return this.request<{ results: any[] }>(
            `/worship/schedule/plans${queryString ? `?${queryString}` : ''}`
        );
    }

    async createPlan(plan: { date: string; event_id?: number; notes?: string }) {
        return this.request<{ plan_id: number; message: string }>('/worship/schedule/plans', {
            method: 'POST',
            body: JSON.stringify(plan),
        });
    }

    async addSetlistSong(planId: number, data: { song_id: number; order_index: number }) {
        return this.request<{ message: string }>(`/worship/schedule/plans/${planId}/setlist`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async assignRoster(planId: number, data: { musician_id: number; instrument: string }) {
        return this.request<{ roster_id: number; message: string }>(`/worship/schedule/plans/${planId}/roster`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateRosterStatus(rosterId: number, status: string) {
        return this.request<{ message: string }>(`/worship/schedule/roster/${rosterId}/status`, {
            method: 'POST',
            body: JSON.stringify({ status }),
        });
    }
}

export const apiClient = new ApiClient();

