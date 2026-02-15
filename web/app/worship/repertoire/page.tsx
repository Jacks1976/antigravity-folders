'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { apiClient } from '@/lib/api-client';
import { useRouter } from 'next/navigation';

export default function RepertoirePage() {
    const { user, token } = useAuth();
    const { t } = useI18n();
    const router = useRouter();

    const [songs, setSongs] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [selectedSong, setSelectedSong] = useState<any>(null);
    const [showAddSong, setShowAddSong] = useState(false);
    const [showAddAsset, setShowAddAsset] = useState(false);
    const [toast, setToast] = useState<string | null>(null);

    // Form states
    const [songForm, setSongForm] = useState({ title: '', artist: '', bpm: '', default_key: '' });
    const [assetForm, setAssetForm] = useState({ type: 'LINK', url: '', label: '', file: null as File | null });

    useEffect(() => {
        if (!token) {
            router.push('/login');
            return;
        }
        loadSongs();
    }, [token, search]);

    const loadSongs = async () => {
        setLoading(true);
        const result = await apiClient.listSongs({ search, limit: 50, offset: 0 });
        if (result.ok && result.data) {
            setSongs(result.data.results || []);
        } else {
            showToast(result.error_key || 'internal_error');
        }
        setLoading(false);
    };

    const showToast = (key: string) => {
        setToast(key);
        setTimeout(() => setToast(null), 3000);
    };

    const handleCreateSong = async (e: React.FormEvent) => {
        e.preventDefault();
        const result = await apiClient.createSong({
            title: songForm.title,
            artist: songForm.artist || undefined,
            bpm: songForm.bpm ? parseInt(songForm.bpm) : undefined,
            default_key: songForm.default_key || undefined,
        });

        if (result.ok) {
            showToast('song.created_success');
            setShowAddSong(false);
            setSongForm({ title: '', artist: '', bpm: '', default_key: '' });
            loadSongs();
        } else {
            showToast(result.error_key || 'internal_error');
        }
    };

    const handleAddAsset = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedSong) return;

        let assetId: number | undefined;

        // If FILE type, upload first
        if (assetForm.type === 'FILE' && assetForm.file) {
            const uploadResult = await apiClient.uploadFile(assetForm.file);
            if (uploadResult.ok && uploadResult.data) {
                assetId = uploadResult.data.asset_id;
            } else {
                showToast(uploadResult.error_key || 'internal_error');
                return;
            }
        }

        const result = await apiClient.addSongAsset(selectedSong.id, {
            type: assetForm.type,
            url: assetForm.type === 'LINK' ? assetForm.url : undefined,
            asset_id: assetId,
            label: assetForm.label || undefined,
        });

        if (result.ok) {
            showToast('song.asset_added');
            setShowAddAsset(false);
            setAssetForm({ type: 'LINK', url: '', label: '', file: null });
            loadSongs();
        } else {
            showToast(result.error_key || 'internal_error');
        }
    };

    if (loading) {
        return <div className="p-8">{t('ui.loading')}</div>;
    }

    return (
        <div className="max-w-6xl mx-auto p-4">
            {toast && (
                <div className="fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded shadow-lg">
                    {t(toast)}
                </div>
            )}

            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">{t('ui.repertoire')}</h1>
                <button
                    onClick={() => setShowAddSong(true)}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                    {t('ui.add_song')}
                </button>
            </div>

            <div className="mb-4">
                <input
                    type="text"
                    placeholder={t('ui.search')}
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full px-4 py-2 border rounded"
                />
            </div>

            {songs.length === 0 ? (
                <p className="text-gray-500">{t('ui.no_results')}</p>
            ) : (
                <div className="grid gap-4">
                    {songs.map((song) => (
                        <div
                            key={song.id}
                            className="border rounded p-4 hover:bg-gray-50 cursor-pointer"
                            onClick={() => setSelectedSong(song)}
                        >
                            <h3 className="font-bold text-lg">{song.title}</h3>
                            {song.artist && <p className="text-gray-600">{song.artist}</p>}
                            <div className="flex gap-4 text-sm text-gray-500 mt-2">
                                {song.default_key && <span>{t('ui.key')}: {song.default_key}</span>}
                                {song.bpm && <span>{t('ui.bpm')}: {song.bpm}</span>}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Add Song Modal */}
            {showAddSong && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full">
                        <h2 className="text-2xl font-bold mb-4">{t('ui.add_song')}</h2>
                        <form onSubmit={handleCreateSong}>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.title')}</label>
                                <input
                                    type="text"
                                    required
                                    value={songForm.title}
                                    onChange={(e) => setSongForm({ ...songForm, title: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.artist')}</label>
                                <input
                                    type="text"
                                    value={songForm.artist}
                                    onChange={(e) => setSongForm({ ...songForm, artist: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.key')}</label>
                                <input
                                    type="text"
                                    value={songForm.default_key}
                                    onChange={(e) => setSongForm({ ...songForm, default_key: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.bpm')}</label>
                                <input
                                    type="number"
                                    value={songForm.bpm}
                                    onChange={(e) => setSongForm({ ...songForm, bpm: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                />
                            </div>
                            <div className="flex gap-2">
                                <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                                    {t('ui.save')}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowAddSong(false)}
                                    className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
                                >
                                    {t('ui.cancel')}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Song Detail Modal */}
            {selectedSong && !showAddAsset && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h2 className="text-2xl font-bold">{selectedSong.title}</h2>
                                {selectedSong.artist && <p className="text-gray-600">{selectedSong.artist}</p>}
                            </div>
                            <button onClick={() => setSelectedSong(null)} className="text-2xl">&times;</button>
                        </div>

                        <div className="flex gap-4 text-sm mb-4">
                            {selectedSong.default_key && <span>{t('ui.key')}: {selectedSong.default_key}</span>}
                            {selectedSong.bpm && <span>{t('ui.bpm')}: {selectedSong.bpm}</span>}
                        </div>

                        <button
                            onClick={() => setShowAddAsset(true)}
                            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 mb-4"
                        >
                            {t('ui.add_asset')}
                        </button>

                        <div className="mt-4">
                            <h3 className="font-bold mb-2">{t('ui.links')}</h3>
                            <p className="text-gray-500 text-sm">{t('ui.no_results')}</p>
                        </div>

                        <div className="mt-4">
                            <h3 className="font-bold mb-2">{t('ui.files')}</h3>
                            <p className="text-gray-500 text-sm">{t('ui.no_results')}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Add Asset Modal */}
            {showAddAsset && selectedSong && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full">
                        <h2 className="text-2xl font-bold mb-4">{t('ui.add_asset')}</h2>
                        <form onSubmit={handleAddAsset}>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.label')}</label>
                                <input
                                    type="text"
                                    value={assetForm.label}
                                    onChange={(e) => setAssetForm({ ...assetForm, label: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">Type</label>
                                <select
                                    value={assetForm.type}
                                    onChange={(e) => setAssetForm({ ...assetForm, type: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                >
                                    <option value="LINK">{t('ui.add_link')}</option>
                                    <option value="FILE">{t('ui.upload_file')}</option>
                                </select>
                            </div>
                            {assetForm.type === 'LINK' ? (
                                <div className="mb-4">
                                    <label className="block mb-2">{t('ui.url')}</label>
                                    <input
                                        type="url"
                                        required
                                        value={assetForm.url}
                                        onChange={(e) => setAssetForm({ ...assetForm, url: e.target.value })}
                                        className="w-full px-4 py-2 border rounded"
                                    />
                                </div>
                            ) : (
                                <div className="mb-4">
                                    <label className="block mb-2">{t('ui.upload_file')}</label>
                                    <input
                                        type="file"
                                        required
                                        accept=".mp3,.pdf"
                                        onChange={(e) => setAssetForm({ ...assetForm, file: e.target.files?.[0] || null })}
                                        className="w-full px-4 py-2 border rounded"
                                    />
                                </div>
                            )}
                            <div className="flex gap-2">
                                <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                                    {t('ui.save')}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowAddAsset(false)}
                                    className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
                                >
                                    {t('ui.cancel')}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
