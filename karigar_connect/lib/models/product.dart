enum UserRole { artisan, buyer, admin }

enum SyncStatus { local, syncing, synced, failed }

class Product {
  const Product({
    required this.id,
    required this.name,
    required this.category,
    required this.description,
    required this.price,
    required this.status,
  });

  final String id;
  final String name;
  final String category;
  final String description;
  final int price;
  final SyncStatus status;

  Product copyWith({
    String? name,
    String? category,
    String? description,
    int? price,
    SyncStatus? status,
  }) {
    return Product(
      id: id,
      name: name ?? this.name,
      category: category ?? this.category,
      description: description ?? this.description,
      price: price ?? this.price,
      status: status ?? this.status,
    );
  }
}