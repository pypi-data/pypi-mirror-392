#include "includes.cpp"


template<typename T>
struct Sparse2DArray {
    std::vector<T> values;
    std::vector<u32> row;
    std::vector<u32> col;
    std::array<u32, 2> shape;
};


template<typename T>
std::vector<T> resize_2d_array(
    const std::vector<T>& data,
    const std::vector<i64>& shape,
    const std::vector<i64>& new_shape
) {
    if (shape.size() != 2 || new_shape.size() != 2) {
        throw std::invalid_argument("resize_2d_array: only 2D arrays are supported");
    }
    
    i64 old_rows = shape[0];
    i64 old_cols = shape[1];
    i64 new_rows = new_shape[0];
    i64 new_cols = new_shape[1];
    
    std::vector<T> new_data(new_rows * new_cols);
    
    // Calculate scaling factors
    f64 row_scale = static_cast<f64>(old_rows - 1) / static_cast<f64>(new_rows - 1);
    f64 col_scale = static_cast<f64>(old_cols - 1) / static_cast<f64>(new_cols - 1);
    
    // Handle edge case of single dimension
    if (new_rows == 1) row_scale = 0.0;
    if (new_cols == 1) col_scale = 0.0;
    
    for (i64 i = 0; i < new_rows; i++) {
        for (i64 j = 0; j < new_cols; j++) {
            // Calculate source coordinates
            f64 src_row = i * row_scale;
            f64 src_col = j * col_scale;
            
            // Get integer parts (floor)
            i64 row0 = static_cast<i64>(src_row);
            i64 col0 = static_cast<i64>(src_col);
            i64 row1 = std::min(row0 + 1, old_rows - 1);
            i64 col1 = std::min(col0 + 1, old_cols - 1);
            
            // Get fractional parts
            f64 row_frac = src_row - row0;
            f64 col_frac = src_col - col0;
            
            // Get the four corner values
            T top_left = data[row0 * old_cols + col0];
            T top_right = data[row0 * old_cols + col1];
            T bottom_left = data[row1 * old_cols + col0];
            T bottom_right = data[row1 * old_cols + col1];
            
            // Bilinear interpolation
            T top = top_left * (1.0 - col_frac) + top_right * col_frac;
            T bottom = bottom_left * (1.0 - col_frac) + bottom_right * col_frac;
            T result = top * (1.0 - row_frac) + bottom * row_frac;
            
            new_data[i * new_cols + j] = result;
        }
    }
    
    return new_data;
}


template<typename T>
Sparse2DArray<T> resize_2d_array(
    const Sparse2DArray<T>& data,
    const std::array<u32, 2>& new_shape
) {
    u32 old_rows = data.shape[0];
    u32 old_cols = data.shape[1];
    u32 new_rows = new_shape[0];
    u32 new_cols = new_shape[1];
    
    Sparse2DArray<T> result;
    result.shape = new_shape;
    
    // Calculate scaling factors
    f64 row_scale = static_cast<f64>(old_rows - 1) / static_cast<f64>(new_rows - 1);
    f64 col_scale = static_cast<f64>(old_cols - 1) / static_cast<f64>(new_cols - 1);
    
    // Handle edge case of single dimension
    if (new_rows == 1) row_scale = 0.0;
    if (new_cols == 1) col_scale = 0.0;
    
    // Build a dense lookup map for the sparse input for efficient access
    std::unordered_map<u64, T> sparse_map;
    for (size_t i = 0; i < data.values.size(); i++) {
        u64 key = (static_cast<u64>(data.row[i]) << 32) | data.col[i];
        sparse_map[key] = data.values[i];
    }
    
    // Helper to get value from sparse map
    auto get_value = [&](u32 row, u32 col) -> T {
        u64 key = (static_cast<u64>(row) << 32) | col;
        auto it = sparse_map.find(key);
        return (it != sparse_map.end()) ? it->second : T(0);
    };
    
    // Process each non-zero element in the input
    // For sparse arrays, we iterate through the non-zero values and their neighborhoods
    std::unordered_map<u64, T> result_map;
    
    for (size_t idx = 0; idx < data.values.size(); idx++) {
        u32 src_row = data.row[idx];
        u32 src_col = data.col[idx];
        T value = data.values[idx];
        
        // Skip zero values
        if (value == T(0)) continue;
        
        // Calculate the range of output pixels influenced by this input pixel
        // Each input pixel can influence multiple output pixels
        u32 out_row_min = static_cast<u32>(std::max(0.0, std::floor(src_row / row_scale - 1)));
        u32 out_row_max = static_cast<u32>(std::min(static_cast<f64>(new_rows - 1), 
                                                                std::ceil(src_row / row_scale + 1)));
        u32 out_col_min = static_cast<u32>(std::max(0.0, std::floor(src_col / col_scale - 1)));
        u32 out_col_max = static_cast<u32>(std::min(static_cast<f64>(new_cols - 1), 
                                                                std::ceil(src_col / col_scale + 1)));
        
        for (u32 out_row = out_row_min; out_row <= out_row_max; out_row++) {
            for (u32 out_col = out_col_min; out_col <= out_col_max; out_col++) {
                // Calculate source coordinates for this output pixel
                f64 src_row_f = out_row * row_scale;
                f64 src_col_f = out_col * col_scale;
                
                // Get integer parts (floor)
                u32 row0 = static_cast<u32>(src_row_f);
                u32 col0 = static_cast<u32>(src_col_f);
                u32 row1 = std::min(row0 + 1, old_rows - 1);
                u32 col1 = std::min(col0 + 1, old_cols - 1);
                
                // Get fractional parts
                f64 row_frac = src_row_f - row0;
                f64 col_frac = src_col_f - col0;
                
                // Get the four corner values
                T top_left = get_value(row0, col0);
                T top_right = get_value(row0, col1);
                T bottom_left = get_value(row1, col0);
                T bottom_right = get_value(row1, col1);
                
                // Bilinear interpolation
                T top = top_left * (1.0 - col_frac) + top_right * col_frac;
                T bottom = bottom_left * (1.0 - col_frac) + bottom_right * col_frac;
                T interpolated = top * (1.0 - row_frac) + bottom * row_frac;
                
                // Store if non-zero
                if (interpolated != T(0)) {
                    u64 key = (static_cast<u64>(out_row) << 32) | out_col;
                    result_map[key] = interpolated;
                }
            }
        }
    }
    
    // Convert map to sparse format
    result.values.reserve(result_map.size());
    result.row.reserve(result_map.size());
    result.col.reserve(result_map.size());
    
    for (const auto& [key, value] : result_map) {
        u32 row = static_cast<u32>(key >> 32);
        u32 col = static_cast<u32>(key & 0xFFFFFFFF);
        result.row.push_back(row);
        result.col.push_back(col);
        result.values.push_back(value);
    }
    
    return result;
}


template<typename T>
class NDArray {

    static i64 get_size_from_shape(const std::vector<i64>& shape) {
        i64 total_size = 1;
        for (i64 dim_size : shape) {
            total_size *= dim_size;
        }
        return total_size;
    }

    // Helper to normalize and validate axis
    i64 normalize_axis(i64 axis, const str& method_name = "") const {
        size_t ndim = shape.size();
        if (axis < 0) {
            axis += static_cast<i64>(ndim);
        }
        if (axis < 0 || axis >= static_cast<i64>(ndim)) {
            throw std::invalid_argument((method_name.empty() ? "axis" : method_name) + ": axis out of bounds");
        }
        return axis;
    }

    // Helper to iterate along an axis and apply operations (const version)
    template<typename OpFunc>
    void iterate_along_axis(i64 axis, OpFunc op_func) const {
        axis = normalize_axis(axis);
        
        std::vector<i64> strides = get_strides();
        i64 axis_size = shape[axis];
        
        // Calculate outer size (product of dimensions before axis)
        i64 outer_size = 1;
        for (i64 i = 0; i < axis; i++) {
            outer_size *= shape[i];
        }
        
        // Calculate inner size (product of dimensions after axis)
        i64 inner_size = 1;
        for (size_t i = axis + 1; i < shape.size(); i++) {
            inner_size *= shape[i];
        }
        
        // Iterate and apply operation
        for (i64 outer = 0; outer < outer_size; outer++) {
            for (i64 inner = 0; inner < inner_size; inner++) {
                // Calculate flat indices for this slice along axis
                std::vector<i64> flat_indices(axis_size);
                for (i64 axis_idx = 0; axis_idx < axis_size; axis_idx++) {
                    i64 flat_idx = 0;
                    i64 temp_outer = outer;
                    for (i64 i = axis - 1; i >= 0; i--) {
                        flat_idx += (temp_outer % shape[i]) * strides[i];
                        temp_outer /= shape[i];
                    }
                    flat_idx += axis_idx * strides[axis];
                    flat_idx += inner;
                    flat_indices[axis_idx] = flat_idx;
                }
                
                // Apply operation to this slice
                op_func(flat_indices);
            }
        }
    }

    // Helper to iterate along an axis and apply operations (non-const version)
    template<typename OpFunc>
    void iterate_along_axis(i64 axis, OpFunc op_func) {
        // Call const version with const_cast to avoid code duplication
        const_cast<const NDArray<T>*>(this)->iterate_along_axis(axis, op_func);
    }

    // Helper for reduction operations along an axis
    template<typename ReduceOp, typename FinalizeOp>
    NDArray<T> reduce_along_axis(
        i64 axis,
        T initial_value,
        ReduceOp reduce_op,
        FinalizeOp finalize_op
    ) const {
        // Reduce all elements
        if (axis == -1) {
            T result = initial_value;
            for (const T& val : data) {
                result = reduce_op(result, val);
            }
            result = finalize_op(result, size());
            return NDArray<T>(std::vector<T>{result}, std::vector<i64>{1});
        }
        
        // Normalize and validate axis
        axis = normalize_axis(axis);
        
        // Calculate new shape (remove the axis dimension)
        std::vector<i64> new_shape;
        for (size_t i = 0; i < shape.size(); i++) {
            if (static_cast<i64>(i) != axis) {
                new_shape.push_back(shape[i]);
            }
        }
        
        // Handle case where result is scalar
        if (new_shape.empty()) {
            new_shape.push_back(1);
        }
        
        i64 new_size = get_size_from_shape(new_shape);
        std::vector<T> new_data(new_size, initial_value);
        i64 axis_size = shape[axis];
        
        // Reduce along axis using iterate_along_axis
        i64 output_idx = 0;
        iterate_along_axis(axis, [&](const std::vector<i64>& indices) {
            T result = initial_value;
            for (i64 flat_idx : indices) {
                result = reduce_op(result, data[flat_idx]);
            }
            new_data[output_idx++] = result;
        });
        
        // Apply finalization operation
        for (T& val : new_data) {
            val = finalize_op(val, axis_size);
        }
        
        return NDArray<T>(std::move(new_data), new_shape);
    }


public:
    std::vector<T> data;
    std::vector<i64> shape;

    NDArray(
        const std::vector<T>& data,
        const std::vector<i64>& shape
    ) : data(data), shape(shape) {}
    NDArray(
        std::vector<T>&& data,
        const std::vector<i64>& shape
    ) : data(std::move(data)), shape(shape) {}
    NDArray(
        const std::vector<i64>& shape,
        const T& initial_value = T()
    ) : shape(shape) {
        data.resize(get_size_from_shape(shape));
        fill(initial_value);
    }

    i64 size() const {
        return static_cast<i64>(data.size());
    }

    const T& operator[](i64 index) const {
        return data[index];
    }
    T& operator[](i64 index) {
        return data[index];
    }

    void fill(const T& value) {
        std::fill(data.begin(), data.end(), value);
    }
    
    NDArray<T> reshape(const std::vector<i64>& new_shape) const {
        i64 new_total_size = 1;
        i64 infer_dim_index = -1;
        for (size_t i = 0; i < new_shape.size(); i++) {
            if (new_shape[i] == -1) {
                if (infer_dim_index != -1) {
                    throw std::invalid_argument("can only specify one unknown dimension in reshape");
                }
                infer_dim_index = static_cast<i64>(i);
            } else if (new_shape[i] <= 0) {
                throw std::invalid_argument("shape dimensions must be positive or -1");
            } else {
                new_total_size *= new_shape[i];
            }
        }
        std::vector<i64> final_shape = new_shape;
        if (infer_dim_index != -1) {
            i64 current_size = size();
            if (current_size % new_total_size != 0) {
                throw std::invalid_argument("reshape array: size mismatch with inferred dimension");
            }
            final_shape[infer_dim_index] = current_size / new_total_size;
            new_total_size = current_size;
        }
        if (new_total_size != size()) {
            throw std::invalid_argument("reshape array: total size must remain the same");
        }
        return NDArray<T>(data, final_shape);
    }

    std::vector<i64> get_strides(const std::vector<i64>* custom_shape = nullptr) const {
        const std::vector<i64>& shape_to_use = custom_shape ? *custom_shape : this->shape;
        size_t ndim = shape_to_use.size();
        if (ndim == 0) return {};
        std::vector<i64> strides(ndim);
        strides[ndim - 1] = 1;
        for (i64 i = static_cast<i64>(ndim) - 2; i >= 0; i--) {
            strides[i] = strides[i + 1] * shape_to_use[i + 1];
        }
        return strides;
    }

    // Transpose the array in-place by permuting dimensions
    // If axes is empty, reverses the order of dimensions (default transpose)
    // Otherwise, permutes dimensions according to the axes vector
    void transpose(const std::vector<i64>& axes = {}) {
        size_t ndim = shape.size();
        
        // Determine the permutation order
        std::vector<i64> perm;
        if (axes.empty()) {
            // Default: reverse all dimensions
            perm.resize(ndim);
            for (size_t i = 0; i < ndim; i++) {
                perm[i] = static_cast<i64>(ndim - 1 - i);
            }
        } else {
            // Use provided axes
            if (axes.size() != ndim) {
                throw std::invalid_argument("transpose: axes length must match number of dimensions");
            }
            perm = axes;
            
            // Validate axes
            std::vector<bool> used(ndim, false);
            for (size_t i = 0; i < ndim; i++) {
                i64 axis = perm[i];
                if (axis < 0 || axis >= static_cast<i64>(ndim)) {
                    throw std::invalid_argument("transpose: axis out of bounds");
                }
                if (used[axis]) {
                    throw std::invalid_argument("transpose: repeated axis");
                }
                used[axis] = true;
            }
        }
        
        // Calculate new shape
        std::vector<i64> new_shape(ndim);
        for (size_t i = 0; i < ndim; i++) {
            new_shape[i] = shape[perm[i]];
        }
        
        // Calculate strides for original and new shape
        std::vector<i64> old_strides = get_strides();
        std::vector<i64> new_strides = get_strides(&new_shape);
        
        // Create transposed data
        std::vector<T> new_data(data.size());
        std::vector<i64> indices(ndim, 0);
        
        for (i64 flat_idx = 0; flat_idx < size(); flat_idx++) {
            // Calculate old multi-dimensional indices
            i64 temp = flat_idx;
            for (size_t i = 0; i < ndim; i++) {
                indices[i] = temp / old_strides[i];
                temp %= old_strides[i];
            }
            
            // Permute indices
            std::vector<i64> new_indices(ndim);
            for (size_t i = 0; i < ndim; i++) {
                new_indices[i] = indices[perm[i]];
            }
            
            // Calculate new flat index
            i64 new_flat_idx = 0;
            for (size_t i = 0; i < ndim; i++) {
                new_flat_idx += new_indices[i] * new_strides[i];
            }
            
            new_data[new_flat_idx] = data[flat_idx];
        }
        
        data = std::move(new_data);
        shape = new_shape;
    }

    // Transpose the array (returns new array)
    // If axes is empty, reverses the order of dimensions (default transpose)
    // Otherwise, permutes dimensions according to the axes vector
    NDArray<T> transposed(const std::vector<i64>& axes = {}) const {
        NDArray<T> result = *this;
        result.transpose(axes);
        return result;
    }    // Flatten the array to 1D
    // Returns a new NDArray with shape {size()}
    NDArray<T> flat() const {
        return NDArray<T>(data, std::vector<i64>{size()});
    }

    // Calculate mean along an optional axis
    // If axis is -1 (default), returns scalar mean of all elements
    // Otherwise, returns NDArray with reduced dimension along specified axis
    NDArray<T> mean(i64 axis = -1) const {
        return reduce_along_axis(
            axis,
            T(),
            [](const T& a, const T& b) { return a + b; },
            [](const T& sum, i64 count) { return sum / static_cast<T>(count); }
        );
    }

    // Calculate minimum along an optional axis
    // If axis is -1 (default), returns scalar minimum of all elements
    // Otherwise, returns NDArray with reduced dimension along specified axis
    NDArray<T> min(i64 axis = -1) const {
        if (data.empty()) {
            throw std::invalid_argument("min: cannot compute minimum of empty array");
        }
        return reduce_along_axis(
            axis,
            std::numeric_limits<T>::max(),
            [](const T& a, const T& b) { return std::min(a, b); },
            [](const T& val, i64) { return val; }
        );
    }

    // Calculate maximum along an optional axis
    // If axis is -1 (default), returns scalar maximum of all elements
    // Otherwise, returns NDArray with reduced dimension along specified axis
    NDArray<T> max(i64 axis = -1) const {
        if (data.empty()) {
            throw std::invalid_argument("max: cannot compute maximum of empty array");
        }
        return reduce_along_axis(
            axis,
            std::numeric_limits<T>::lowest(),
            [](const T& a, const T& b) { return std::max(a, b); },
            [](const T& val, i64) { return val; }
        );
    }

    // Calculate quantile along an optional axis
    // q: quantile value between 0 and 1 (e.g., 0.5 for median)
    // axis: axis along which to compute quantile (-1 for all elements)
    // If axis is -1 (default), returns scalar quantile of all elements
    // Otherwise, returns NDArray with reduced dimension along specified axis
    NDArray<T> quantile(f64 q, i64 axis = -1) const {
        if (data.empty()) {
            throw std::invalid_argument("quantile: cannot compute quantile of empty array");
        }
        if (q < 0.0 || q > 1.0) {
            throw std::invalid_argument("quantile: q must be between 0 and 1");
        }
        
        size_t ndim = shape.size();
        
        // Compute quantile of all elements
        if (axis == -1) {
            std::vector<T> sorted_data = data;
            std::sort(sorted_data.begin(), sorted_data.end());
            
            f64 pos = q * (sorted_data.size() - 1);
            size_t lower_idx = static_cast<size_t>(std::floor(pos));
            size_t upper_idx = static_cast<size_t>(std::ceil(pos));
            
            T result;
            if (lower_idx == upper_idx) {
                result = sorted_data[lower_idx];
            } else {
                f64 weight = pos - lower_idx;
                result = sorted_data[lower_idx] * (1.0 - weight) + sorted_data[upper_idx] * weight;
            }
            
            return NDArray<T>(std::vector<T>{result}, std::vector<i64>{1});
        }
        
        // Normalize negative axis
        if (axis < 0) {
            axis += static_cast<i64>(ndim);
        }
        
        // Validate axis
        if (axis < 0 || axis >= static_cast<i64>(ndim)) {
            throw std::invalid_argument("quantile: axis out of bounds");
        }
        
        // Calculate new shape (remove the axis dimension)
        std::vector<i64> new_shape;
        for (size_t i = 0; i < ndim; i++) {
            if (static_cast<i64>(i) != axis) {
                new_shape.push_back(shape[i]);
            }
        }
        
        // Handle case where result is scalar
        if (new_shape.empty()) {
            new_shape.push_back(1);
        }
        
        i64 new_size = get_size_from_shape(new_shape);
        std::vector<T> new_data(new_size);
        
        // Calculate strides
        std::vector<i64> strides = get_strides();
        i64 axis_size = shape[axis];
        
        // For each output element, collect values along axis and compute quantile
        std::vector<i64> indices(ndim, 0);
        std::vector<T> temp_values;
        temp_values.reserve(axis_size);
        
        for (i64 out_idx = 0; out_idx < new_size; out_idx++) {
            // Calculate the multi-dimensional index for this output element
            i64 temp = out_idx;
            std::vector<i64> out_indices(new_shape.size());
            for (i64 i = static_cast<i64>(new_shape.size()) - 1; i >= 0; i--) {
                out_indices[i] = temp % new_shape[i];
                temp /= new_shape[i];
            }
            
            // Map back to original indices (insert axis dimension)
            size_t out_dim_idx = 0;
            for (size_t i = 0; i < ndim; i++) {
                if (static_cast<i64>(i) == axis) {
                    indices[i] = 0; // Will iterate over this
                } else {
                    indices[i] = out_indices[out_dim_idx++];
                }
            }
            
            // Collect all values along the axis
            temp_values.clear();
            for (i64 axis_idx = 0; axis_idx < axis_size; axis_idx++) {
                indices[axis] = axis_idx;
                
                // Calculate flat index
                i64 flat_idx = 0;
                for (size_t i = 0; i < ndim; i++) {
                    flat_idx += indices[i] * strides[i];
                }
                
                temp_values.push_back(data[flat_idx]);
            }
            
            // Sort and compute quantile
            std::sort(temp_values.begin(), temp_values.end());
            
            f64 pos = q * (temp_values.size() - 1);
            size_t lower_idx = static_cast<size_t>(std::floor(pos));
            size_t upper_idx = static_cast<size_t>(std::ceil(pos));
            
            if (lower_idx == upper_idx) {
                new_data[out_idx] = temp_values[lower_idx];
            } else {
                f64 weight = pos - lower_idx;
                new_data[out_idx] = temp_values[lower_idx] * (1.0 - weight) + temp_values[upper_idx] * weight;
            }
        }
        
        return NDArray<T>(std::move(new_data), new_shape);
    }

    // Generic generator for iterating over slices along any axis
    class AxisIterator : public GeneratorBase<AxisIterator, NDArray<T>> {
        const NDArray<T>* array;
        i64 axis;
        i64 axis_size;
        i64 current_slice;
        std::vector<i64> strides;
        i64 outer_size;
        i64 inner_size;
        std::vector<i64> slice_shape;

    public:
        AxisIterator(const NDArray<T>* arr, i64 ax) 
            : array(arr), axis(ax), current_slice(0) {
            
            // Normalize and validate axis
            axis = array->normalize_axis(axis, "iter_axis");
            
            strides = array->get_strides();
            axis_size = array->shape[axis];
            
            // Calculate outer size (product of dimensions before axis)
            outer_size = 1;
            for (i64 i = 0; i < axis; i++) {
                outer_size *= array->shape[i];
            }
            
            // Calculate inner size (product of dimensions after axis)
            inner_size = 1;
            for (size_t i = axis + 1; i < array->shape.size(); i++) {
                inner_size *= array->shape[i];
            }
            
            // Calculate slice shape (remove the iterated axis)
            for (size_t i = 0; i < array->shape.size(); i++) {
                if (static_cast<i64>(i) != axis) {
                    slice_shape.push_back(array->shape[i]);
                }
            }
            
            // Handle case where slice is scalar (1D array iterated)
            if (slice_shape.empty()) {
                slice_shape.push_back(1);
            }
        }

        typename GeneratorBase<AxisIterator, NDArray<T>>::NextResult next() {
            if (current_slice >= axis_size) {
                return {NDArray<T>({}, {}), true};
            }
            
            // Calculate total size of the slice
            i64 slice_size = outer_size * inner_size;
            std::vector<T> slice_data;
            slice_data.reserve(slice_size);
            
            // Collect data for this slice
            for (i64 outer = 0; outer < outer_size; outer++) {
                for (i64 inner = 0; inner < inner_size; inner++) {
                    // Calculate flat index for this element
                    i64 flat_idx = 0;
                    i64 temp_outer = outer;
                    for (i64 i = axis - 1; i >= 0; i--) {
                        flat_idx += (temp_outer % array->shape[i]) * strides[i];
                        temp_outer /= array->shape[i];
                    }
                    flat_idx += current_slice * strides[axis];
                    flat_idx += inner;
                    
                    slice_data.push_back(array->data[flat_idx]);
                }
            }
            
            current_slice++;
            return {NDArray<T>(std::move(slice_data), slice_shape), false};
        }
    };

    // Iterate over slices along any axis (returns generator)
    // For a 3D array with shape {3, 4, 5}:
    // - iter_axis(0) yields 3 slices of shape {4, 5}
    // - iter_axis(1) yields 4 slices of shape {3, 5}
    // - iter_axis(2) yields 5 slices of shape {3, 4}
    AxisIterator iter_axis(i64 axis) const {
        return AxisIterator(this, axis);
    }

    // Iterate over rows (first dimension) - convenience method
    AxisIterator iter_rows() const {
        return iter_axis(0);
    }

    // Iterate over columns (second dimension) - convenience method
    // Only meaningful for 2D+ arrays
    AxisIterator iter_cols() const {
        if (shape.size() < 2) {
            throw std::invalid_argument("iter_cols: array must have at least 2 dimensions");
        }
        return iter_axis(1);
    }

    // Sort the array in-place
    // If axis is -1 (default), sorts the flattened array
    // Otherwise, sorts along the specified axis
    void sort(i64 axis = -1) {
        // Sort flattened array
        if (axis == -1) {
            std::sort(data.begin(), data.end());
            return;
        }
        
        // Sort along axis using helper
        std::vector<T> temp_values(shape[axis]);
        iterate_along_axis(axis, [&](const std::vector<i64>& indices) {
            // Collect values
            for (size_t i = 0; i < indices.size(); i++) {
                temp_values[i] = data[indices[i]];
            }
            // Sort
            std::sort(temp_values.begin(), temp_values.end());
            // Write back
            for (size_t i = 0; i < indices.size(); i++) {
                data[indices[i]] = temp_values[i];
            }
        });
    }

    // Sort the array (returns new array)
    // If axis is -1 (default), sorts the flattened array
    // Otherwise, sorts along the specified axis
    NDArray<T> sorted(i64 axis = -1) const {
        NDArray<T> result = *this;
        result.sort(axis);
        return result;
    }

    // Reverse the array in-place
    // If axis is -1 (default), reverses the flattened array
    // Otherwise, reverses along the specified axis
    void reverse(i64 axis = -1) {
        // Reverse flattened array
        if (axis == -1) {
            std::reverse(data.begin(), data.end());
            return;
        }
        
        // Reverse along axis using helper
        iterate_along_axis(axis, [&](const std::vector<i64>& indices) {
            // Reverse by swapping from both ends
            size_t n = indices.size();
            for (size_t i = 0; i < n / 2; i++) {
                std::swap(data[indices[i]], data[indices[n - 1 - i]]);
            }
        });
    }

    // Reverse the array (returns new array)
    // If axis is -1 (default), reverses the flattened array
    // Otherwise, reverses along the specified axis
    NDArray<T> reversed(i64 axis = -1) const {
        NDArray<T> result = *this;
        result.reverse(axis);
        return result;
    }

    




};
