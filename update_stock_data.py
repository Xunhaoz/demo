import modules.get_stock as get_stock
import modules.store_feature_sqlite as store_feature_sqlite
import modules.kmeans_allocation as kmeans_allocation
import modules.round_robin as round_robin

if __name__ == "__main__":
    get_stock.get_stock()

    store_feature_sqlite.store_feature_sqlite()

    kmeans_allocation.kmeans_allocation()

    round_robin.round_robin()