import { createClient } from '@supabase/supabase-js';

// Access environment variables
const supabaseUrl = import.meta.env.VITE_DB_URL;
const supabaseKey = import.meta.env.VITE_DB_KEY;

// Create and export the Supabase client
const supabase = createClient(supabaseUrl, supabaseKey);

export default supabase;
