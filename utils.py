from collections import defaultdict


def get_entities(observed, sep=' ', output_col=1):
    """Get entities from file."""
    example = 0
    word_index = 0
    entity = []
    last_ne = 'O'
    last_sent = ''
    last_entity = []

    observations = defaultdict(defaultdict)
    observations[example] = []

    for line in observed:
        line = line.strip()
        if line.startswith('##'):
            continue
        elif len(line) == 0:
            if entity:
                observations[example].append(list(entity))
                entity = []

            example += 1
            observations[example] = []
            word_index = 0
            last_ne = 'O'
            continue

        split_line = line.split(sep)
        # word = split_line[0]
        value = split_line[output_col]
        ne = value[0]
        sent = value[2:]

        last_entity = []

        # check if it is start of entity
        if ne == 'B' or (ne == 'I' and last_ne == 'O') or \
                (ne == 'I' and last_ne != 'O' and last_sent != sent):
            if entity:
                last_entity = entity
            entity = [sent]
            entity.append(word_index)
        elif ne == 'I':
            entity.append(word_index)
        elif ne == 'O':
            if last_ne == 'B' or last_ne == 'I':
                last_entity = entity
            entity = []

        if last_entity:
            observations[example].append(list(last_entity))
            last_entity = []

        last_ne = ne
        last_sent = sent
        word_index += 1

    if entity:
        observations[example].append(list(entity))

    return observations


def compare_result(observed, predicted):
    """Compare bewteen gold data and prediction data."""
    total_observed = 0
    total_predicted = 0
    correct = {'entities': 0, 'sentiment': 0}

    for example in observed:
        observed_instance = observed[example]
        predicted_instance = predicted[example]
        total_observed += len(observed_instance)
        total_predicted += len(predicted_instance)

        for span in predicted_instance:
            span_sent = span[0]
            span_ne = (span[1], len(span) - 1)

            for observed_span in observed_instance:
                sent = observed_span[0]
                ne = (observed_span[1], len(observed_span) - 1)

                if span_ne == ne:
                    correct['entities'] += 1
                    if span_sent == sent:
                        correct['sentiment'] += 1

    print('Entities in gold data : %d' % total_observed)
    print('Entities in prediction: %d' % total_predicted)

    for t in ('entities', 'sentiment'):
        print()
        prec = correct[t] / total_predicted
        recl = correct[t] / total_observed
        try:
            f = 2 * prec * recl / (prec + recl)
        except ZeroDivisionError:
            f = 0
        print(t)
        print(' - Correct   : %d' % correct[t])
        print(' - Precision : %.4f' % prec)
        print(' - Recall    : %.4f' % recl)
        print(' - F score   : %.4f' % f)


def load_file(filename):
    sentences = []

    with open(filename) as f:
        # new sentence
        s = []

        for l in f:
            l = l.strip()

            # add word to sentence
            if l:
                s.append(tuple(l.rsplit(' ', 1)))
                continue

            # sentence complete
            sentences.append(tuple(s))
            s = []

    return tuple(sentences)
