# NoLess Examples

This directory contains example configurations and usage patterns for NoLess.

## Quick Start Examples

### 1. Image Classification

Search for an image dataset:
```bash
noless search --query "image classification flowers"
```

Create an image classification project:
```bash
noless create --task image-classification --framework pytorch --output ./my_flower_classifier
```

### 2. Text Classification

Search for text datasets:
```bash
noless search --query "sentiment analysis twitter" --source huggingface
```

Create a text classification project:
```bash
noless create --task text-classification --framework pytorch --architecture bert --output ./sentiment_model
```

### 3. Object Detection

Create an object detection project:
```bash
noless create --task object-detection --framework pytorch --output ./detector
```

### 4. Custom Model

Generate a custom training script:
```bash
noless generate --model-type transformer --task nlp --framework pytorch --output ./custom_train.py
```

## Configuration Examples

See `config_example.yaml` for a complete configuration reference.

## Tips

1. **Start Small**: Begin with a small dataset and few epochs to test your setup
2. **Monitor Training**: Use TensorBoard or similar tools to track metrics
3. **GPU Usage**: Enable CUDA if you have a compatible GPU for faster training
4. **Data Preparation**: Ensure your data is properly formatted before training
5. **Hyperparameter Tuning**: Adjust learning rate, batch size, and architecture based on results

## Common Workflows

### Complete Workflow Example

```bash
# 1. Search for dataset
noless search --query "cats and dogs classification"

# 2. Create project
noless create --task image-classification --framework pytorch --dataset "cats-vs-dogs" --output ./cat_dog_classifier

# 3. Navigate to project
cd cat_dog_classifier

# 4. Review and edit configuration
# Edit config.yaml as needed

# 5. Start training
python train.py

# 6. Evaluate results
# Model will be saved as best_model.pth
```

## Support

For more information, see the main README.md or visit our documentation.
