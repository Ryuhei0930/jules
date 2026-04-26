// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "OpenClaw",
    platforms: [
        .iOS(.v18),
        .macOS(.v15)
    ],
    products: [
        .library(
            name: "OpenClawApp",
            targets: ["OpenClawApp"]),
    ],
    dependencies: [
        .package(url: "https://github.com/pvieito/PythonKit.git", from: "0.3.1"),
        .package(url: "https://github.com/ml-explore/mlx-swift.git", from: "0.19.0")
    ],
    targets: [
        .target(
            name: "OpenClawApp",
            dependencies: [
                "PythonKit",
                .product(name: "MLX", package: "mlx-swift")
            ]),
        .testTarget(
            name: "OpenClawAppTests",
            dependencies: ["OpenClawApp"]),
    ]
)