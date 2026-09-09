import 'package:flutter_test/flutter_test.dart';

import 'package:karigar_connect/models/product.dart';
import 'package:karigar_connect/services/app_repository.dart';
import 'package:karigar_connect/services/catalog_service.dart';

void main() {
  test('catalog service creates a conservative local draft', () async {
    final product = await CatalogService().generateFromText('A handwoven cotton saree in blue');

    expect(product.category, 'Textiles');
    expect(product.name, 'A handwoven cotton saree');
    expect(product.status, SyncStatus.local);
  });

  test('catalog service rejects empty voice or text input', () {
    expect(() => CatalogService().generateFromText('   '), throwsFormatException);
  });

  test('repository stores a draft with local sync status', () async {
    const draft = Product(
      id: 'draft-1',
      name: 'Clay pot',
      category: 'Pottery',
      description: 'A hand-shaped clay pot.',
      price: 0,
      status: SyncStatus.synced,
    );
    final repository = AppRepository();

    await repository.saveDraft(draft);

    expect(repository.products.last.id, 'draft-1');
    expect(repository.products.last.status, SyncStatus.local);
  });
}