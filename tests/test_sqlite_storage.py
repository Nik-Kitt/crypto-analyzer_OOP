import copy


def test_create_tables(sqlite_storage):
    connection = sqlite_storage.connection
    cursor = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table';
    """)
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(row[0])

    assert 'coin_prices' in result
    assert 'snapshots' in result


def test_save_snapshot(sqlite_storage, sample_results):
    sqlite_storage.save(sample_results)

    connection = sqlite_storage.connection
    cursor = connection.execute("""
        SELECT generated_at, total_coins_analyzed, total_market_cap_usd
        FROM snapshots;
    """)
    result = cursor.fetchone()

    assert result == (
        sample_results['generated_at'],
        sample_results['total_coins_analyzed'],
        sample_results['total_market_cap_usd']
    )


def test_save_coin_prices(sqlite_storage, sample_results):
    sqlite_storage.save(sample_results)

    connection = sqlite_storage.connection
    cursor = connection.execute("""
        SELECT name, category
        FROM coin_prices
        ORDER BY id;
    """)
    result = cursor.fetchall()

    assert result == [
        ('Bitcoin', 'gainer'),
        ('Ethereum', 'loser')
    ]


def test_save_creates_new_snapshot(sqlite_storage, sample_results):
    sqlite_storage.save(sample_results)
    sqlite_storage.save(sample_results)

    connection = sqlite_storage.connection
    cursor = connection.execute("""
        SELECT COUNT(*) FROM snapshots;
    """)
    result = cursor.fetchone()[0]

    assert result == 2


def test_get_snapshots(sqlite_storage, sample_results):
    sqlite_storage.save(sample_results)
    sqlite_storage.save(sample_results)

    result = sqlite_storage.get_snapshots()

    assert len(result) == 2
    assert result[0]['id'] == 1
    assert result[1]['id'] == 2


def test_get_price_history(sqlite_storage, sample_results):
    sqlite_storage.save(sample_results)
    sqlite_storage.save(sample_results)

    result = sqlite_storage.get_price_history('Bitcoin')

    assert len(result) == 2
    assert result[0]['name'] == 'Bitcoin'
    assert result[0]['current_price'] == 100000.0
    assert result[1]['current_price'] == 100000.0
    assert result[0]['generated_at'] == '2026-11-07 10:00:00'


def test_compare_snapshots(sqlite_storage, sample_results):
    sqlite_storage.save(sample_results)

    sample_result_2 = copy.deepcopy(sample_results)
    sample_result_2['top_gainers'][0]['current_price'] = 105000.0

    sqlite_storage.save(sample_result_2)

    result = sqlite_storage.compare_snapshots(1, 2)

    assert result[0]['name'] == 'Bitcoin'
    assert result[0]['old_price'] == 100000.0
    assert result[0]['new_price'] == 105000.0
    assert result[0]['price_difference'] == 5000.0


def test_get_top_gainers(sqlite_storage, sample_results):
    sqlite_storage.save(sample_results)

    result = sqlite_storage.get_top_gainers(5)

    assert len(result) == 1
    assert result[0]['name'] == 'Bitcoin'
    assert result[0]['change_24h'] > 0


def test_get_top_losers(sqlite_storage, sample_results):
    sqlite_storage.save(sample_results)

    result = sqlite_storage.get_top_losers(5)

    assert len(result) == 1
    assert result[0]['name'] == 'Ethereum'
    assert result[0]['change_24h'] < 0
