import '../models/product.dart';

class AppRepository {
  final List<Product> _products = [
    const Product(
      id: 'demo-1',
      name: 'Blue handwoven saree',
      category: 'Textiles',
      description: 'A handwoven cotton saree in blue.',
      price: 1400,
      status: SyncStatus.synced,
    ),
  ];

  List<Product> get products => List.unmodifiable(_products);

  Future<void> saveDraft(Product product) async {
    final index = _products.indexWhere((item) => item.id == product.id);
    if (index == -1) {
      _products.add(product.copyWith(status: SyncStatus.local));
    } else {
      _products[index] = product.copyWith(status: SyncStatus.local);
    }
  }

  Future<void> publish(Product product) async {
    final index = _products.indexWhere((item) => item.id == product.id);
    final published = product.copyWith(status: SyncStatus.synced);
    if (index == -1) {
      _products.add(published);
    } else {
      _products[index] = published;
    }
  }
}