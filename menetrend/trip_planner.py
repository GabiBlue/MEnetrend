def dijkstra(graph, src, dest, visited=[], distances={}, predecessors={}):
    """ calculates a shortest path tree routed in src
    """
    # a few sanity checks
    if src['name'] not in graph:
        raise TypeError('The root of the shortest path tree cannot be found')
    if dest not in graph:
        raise TypeError('The target of the shortest path cannot be found')
        # ending condition
    if src['name'] == dest:
        # We build the shortest path and display it
        path = []
        pred = {'name': dest, 'route': None}
        while pred != None:
            path.append(pred)
            pred = predecessors.get(pred['name'], None)

        for i in graph[path[-1]['name']]:
            if i['route'] == path[-2]['route']:
                path[-1]['route'] = path[-2]['route']

        return path, distances[dest]
    else:
        # if it is the initial  run, initializes the cost
        if not visited:
            distances[src['name']] = {'cost': 0, 'route': None}
        # visit the neighbors
        for neighbor in graph[src['name']]:
            if neighbor['name'] not in visited:
                new_distance = distances[src['name']]['cost'] + neighbor['cost']
                temp = distances.get(neighbor['name'], float('inf'))
                if temp != float('inf'):
                    temp = temp['cost']
                # if new_distance < distances.get(neighbor['name'], float('inf')):
                if new_distance < temp:
                    distances[neighbor['name']] = {'cost': new_distance, 'route': neighbor['route']}
                    predecessors[neighbor['name']] = src
        # mark as visited
        visited.append(src)
        # now that all neighbors have been visited: recurse
        # select the non visited node with lowest distance 'x'
        # run Dijskstra with src='x'
        unvisited = {}
        for k in graph:
            if not any(d['name'] == k for d in visited):
                # if k not in visited.values():
                unvisited[k] = distances.get(k, {'cost': float('inf'), 'route': None})
        min_value = min(unvisited.values(), key=lambda x: x['cost'])
        min_name = min(unvisited.keys(), key=lambda x: unvisited[x]['cost'])
        new_src = {'name': min_name, 'route': min_value['route']}
        return dijkstra(graph, new_src, dest, visited, distances, predecessors)
