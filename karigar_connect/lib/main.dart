import 'package:flutter/material.dart';

import 'models/product.dart';
import 'services/app_repository.dart';
import 'services/catalog_service.dart';

void main() {
  runApp(const KarigarConnectApp());
}

class KarigarConnectApp extends StatelessWidget {
  const KarigarConnectApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'KarigarConnect',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff9d3f2e)),
        scaffoldBackgroundColor: const Color(0xfff8f4ec),
        useMaterial3: true,
        textTheme: const TextTheme(
          headlineMedium: TextStyle(fontWeight: FontWeight.w800),
          titleLarge: TextStyle(fontWeight: FontWeight.w700),
        ),
      ),
      home: const RoleScreen(),
    );
  }
}

class RoleScreen extends StatelessWidget {
  const RoleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 520),
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Icon(Icons.handshake_outlined, size: 72, color: Color(0xff9d3f2e)),
                  const SizedBox(height: 20),
                  Text('KarigarConnect', style: Theme.of(context).textTheme.headlineMedium),
                  const SizedBox(height: 8),
                  const Text('From your craft to more customers.', style: TextStyle(fontSize: 18)),
                  const SizedBox(height: 40),
                  _RoleButton(
                    icon: Icons.storefront_outlined,
                    label: 'I am an artisan',
                    onPressed: () => _openHome(context, UserRole.artisan),
                  ),
                  const SizedBox(height: 14),
                  _RoleButton(
                    icon: Icons.shopping_bag_outlined,
                    label: 'I am a buyer',
                    onPressed: () => _openHome(context, UserRole.buyer),
                  ),
                  const SizedBox(height: 14),
                  TextButton.icon(
                    onPressed: () => _openHome(context, UserRole.admin),
                    icon: const Icon(Icons.admin_panel_settings_outlined),
                    label: const Text('Admin workspace'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _openHome(BuildContext context, UserRole role) {
    Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => HomeScreen(role: role)));
  }
}

class _RoleButton extends StatelessWidget {
  const _RoleButton({required this.icon, required this.label, required this.onPressed});

  final IconData icon;
  final String label;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return FilledButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 28),
      label: Padding(padding: const EdgeInsets.all(16), child: Text(label, style: const TextStyle(fontSize: 18))),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({required this.role, super.key});

  final UserRole role;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final AppRepository _repository = AppRepository();

  @override
  Widget build(BuildContext context) {
    final isArtisan = widget.role == UserRole.artisan;
    final isBuyer = widget.role == UserRole.buyer;
    return Scaffold(
      appBar: AppBar(title: Text(isArtisan ? 'My workshop' : isBuyer ? 'Marketplace' : 'Admin overview')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(isArtisan ? 'Create something beautiful' : isBuyer ? 'Find handmade work' : 'Keep the marketplace healthy', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          Text(isArtisan ? 'Use your camera or voice to add a product.' : 'Browse products made by local artisans.'),
          const SizedBox(height: 24),
          if (isArtisan) ...[
            FilledButton.icon(onPressed: _addProduct, icon: const Icon(Icons.add_a_photo_outlined), label: const Padding(padding: EdgeInsets.all(14), child: Text('Add a product', style: TextStyle(fontSize: 18)))),
            const SizedBox(height: 24),
            const Text('My products', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            ..._repository.products.map(_productTile),
          ] else ...[
            const _InfoTile(icon: Icons.search, title: 'Marketplace search', detail: 'Search and filter products once the central API is configured.'),
            const _InfoTile(icon: Icons.favorite_border, title: 'Recommendations', detail: 'Personalized recommendations will come from the marketplace service.'),
            const _InfoTile(icon: Icons.mail_outline, title: 'Enquiries', detail: 'Buyer and artisan enquiries will be stored by the central backend.'),
          ],
        ],
      ),
    );
  }

  Widget _productTile(Product product) {
    return Card(
      child: ListTile(
        leading: const CircleAvatar(child: Icon(Icons.category_outlined)),
        title: Text(product.name),
        subtitle: Text('${product.category} - ${_statusLabel(product.status)}'),
        trailing: product.price == 0 ? const Text('Price pending') : Text('INR ${product.price}'),
      ),
    );
  }

  Future<void> _addProduct() async {
    final product = await Navigator.of(context).push<Product>(MaterialPageRoute(builder: (_) => const AddProductScreen()));
    if (product == null || !mounted) return;
    await _repository.saveDraft(product);
    if (!mounted) return;
    setState(() {});
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Saved locally as a draft.')));
  }

  String _statusLabel(SyncStatus status) => switch (status) {
        SyncStatus.local => 'Saved locally',
        SyncStatus.syncing => 'Syncing',
        SyncStatus.synced => 'Synced',
        SyncStatus.failed => 'Sync failed',
      };
}

class AddProductScreen extends StatefulWidget {
  const AddProductScreen({super.key});

  @override
  State<AddProductScreen> createState() => _AddProductScreenState();
}

class _AddProductScreenState extends State<AddProductScreen> {
  final TextEditingController _detailsController = TextEditingController();
  final CatalogService _catalogService = CatalogService();
  Product? _draft;
  String? _error;

  @override
  void dispose() {
    _detailsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add product')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          OutlinedButton.icon(onPressed: () {}, icon: const Icon(Icons.camera_alt_outlined, size: 30), label: const Padding(padding: EdgeInsets.all(14), child: Text('Take a product photo'))),
          const SizedBox(height: 12),
          const Text('Image processing will connect to M3 when the service URL is configured.'),
          const SizedBox(height: 24),
          TextField(
            controller: _detailsController,
            maxLines: 4,
            decoration: const InputDecoration(labelText: 'Tell us about your product', hintText: 'You can type or speak here', border: OutlineInputBorder()),
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(onPressed: () {}, icon: const Icon(Icons.mic_none), label: const Text('Speak product details')),
          const SizedBox(height: 20),
          FilledButton.icon(onPressed: _generate, icon: const Icon(Icons.auto_awesome), label: const Padding(padding: EdgeInsets.all(14), child: Text('Create catalog details'))),
          if (_error != null) Padding(padding: const EdgeInsets.only(top: 16), child: Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error))),
          if (_draft != null) ...[
            const SizedBox(height: 24),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(_draft!.name, style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: 8),
                      Text(_draft!.category),
                      const SizedBox(height: 8),
                      Text(_draft!.description),
                      const SizedBox(height: 16),
                      const Text('Price suggestion will connect to M5.'),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 12),
            FilledButton(onPressed: () => Navigator.of(context).pop(_draft), child: const Padding(padding: EdgeInsets.all(14), child: Text('Save draft'))),
          ],
        ],
      ),
    );
  }

  Future<void> _generate() async {
    try {
      final product = await _catalogService.generateFromText(_detailsController.text);
      setState(() {
        _draft = product;
        _error = null;
      });
    } on FormatException catch (error) {
      setState(() => _error = error.message);
    }
  }
}

class _InfoTile extends StatelessWidget {
  const _InfoTile({required this.icon, required this.title, required this.detail});

  final IconData icon;
  final String title;
  final String detail;

  @override
  Widget build(BuildContext context) {
    return Card(child: ListTile(leading: Icon(icon, size: 30), title: Text(title), subtitle: Text(detail)));
  }
}