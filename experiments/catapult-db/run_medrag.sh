
cargo run --release -- -q medrag-zipf-reshuffled-f32.npy --graph pubmed35/ann --payload pubmed35/ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/medrag_catapult.json --mode catapult
cargo run --release -- -q medrag-zipf-reshuffled-f32.npy --graph pubmed35/ann --payload pubmed35/ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/medrag_vanilla.json --mode vanilla
cargo run --release -- -q medrag-zipf-reshuffled-f32.npy --graph pubmed35/ann --payload pubmed35/ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/medrag_lshapg.json --mode lshapg


cargo run --release -- -q medrag-zipf-reshuffled-f32.npy --graph pubmed35/ann --payload pubmed35/ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/medrag_catapult_neighbors.json --mode catapult --output-neighbors
cargo run --release -- -q medrag-zipf-reshuffled-f32.npy --graph pubmed35/ann --payload pubmed35/ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/medrag_vanilla_neighbors.json --mode vanilla --output-neighbors
cargo run --release -- -q medrag-zipf-reshuffled-f32.npy --graph pubmed35/ann --payload pubmed35/ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/medrag_lshapg_neighbors.json --mode lshapg --output-neighbors

cargo run --release -- -q medrag-zipf-reshuffled-f32.npy --graph pubmed35/ann --payload pubmed35/ann.data -t 62 --beam-width 64 --seeds 42 --output ./results/medrag_ground_truth.json --mode vanilla --output-neighbors
