/** Build only the explicitly selected local synthetic API test database. */
import setup from '../../database/tests/support/api-global-setup.js';

await setup();
process.stdout.write('Synthetic backend test database prepared.\n');
